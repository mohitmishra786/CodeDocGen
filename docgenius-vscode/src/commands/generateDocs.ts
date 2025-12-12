import * as vscode from 'vscode';
import * as child_process from 'child_process';
import * as path from 'path';
import { promisify } from 'util';

const exec = promisify(child_process.exec);

export async function generateForFile(
    context: vscode.ExtensionContext,
    scope: 'file' | 'selection' | 'workspace',
    document?: vscode.TextDocument
) {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor && scope !== 'workspace') {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }

        const doc = document || (editor ? editor.document : undefined);
        if (!doc && scope !== 'workspace') {
            return;
        }

        // Get configuration
        const config = vscode.workspace.getConfiguration('docgenius');
        const pythonPath = config.get<string>('pythonPath', 'python');
        const aiEnabled = config.get<boolean>('ai.enabled', false);
        const aiProvider = config.get<string>('ai.provider', 'nltk');
        const showPreview = config.get<boolean>('showPreviewBeforeApplying', true);
        const clangPath = config.get<string>('clangPath', '');
        const maxWorkers = config.get<number>('maxWorkers', 4);
        const enableCache = config.get<boolean>('enableCache', true);

        // Determine what to process
        let targetPath: string;
        let targetFiles: string[] = [];

        if (scope === 'workspace') {
            const workspaceFolders = vscode.workspace.workspaceFolders;
            if (!workspaceFolders) {
                vscode.window.showErrorMessage('No workspace folder open');
                return;
            }
            targetPath = workspaceFolders[0].uri.fsPath;
        } else if (doc) {
            targetPath = path.dirname(doc.uri.fsPath);
            targetFiles = [doc.uri.fsPath];
        } else {
            return;
        }

        // Build command
        const codeDocGenPath = 'code_doc_gen';  // Assumes installed globally or in PATH
        let command = `${pythonPath} -m ${codeDocGenPath} --repo "${targetPath}"`;

        if (targetFiles.length > 0 && scope === 'file') {
            command += ` --files "${targetFiles[0]}"`;
        }

        if (aiEnabled) {
            command += ` --enable-ai --ai-provider ${aiProvider}`;
        }

        if (clangPath) {
            command += ` --clang-path "${clangPath}"`;
        }

        command += ` --max-workers ${maxWorkers}`;

        if (enableCache) {
            command += ` --enable-cache`;
        }

        if (showPreview) {
            command += ` --diff`;
        } else {
            command += ` --inplace`;
        }

        // Show progress
        await vscode.window.withProgress(
            {
                location: vscode.ProgressLocation.Notification,
                title: `DocGenius: Generating documentation for ${scope}`,
                cancellable: false
            },
            async (progress) => {
                progress.report({ increment: 0 });

                try {
                    const { stdout, stderr } = await exec(command);

                    if (stderr) {
                        console.error('DocGenius stderr:', stderr);
                    }

                    if (showPreview && stdout) {
                        // Show diff in output channel
                        const outputChannel = vscode.window.createOutputChannel('DocGenius Diff');
                        outputChannel.appendLine(stdout);
                        outputChannel.show();

                        // Ask user to apply changes
                        const apply = await vscode.window.showInformationMessage(
                            'Documentation generated. Apply changes?',
                            'Apply',
                            'Cancel'
                        );

                        if (apply === 'Apply') {
                            // Re-run without --diff
                            const applyCommand = command.replace('--diff', '--inplace');
                            await exec(applyCommand);
                            vscode.window.showInformationMessage('Documentation applied successfully');

                            // Reload document
                            if (doc) {
                                const document = await vscode.workspace.openTextDocument(doc.uri);
                                await vscode.window.showTextDocument(document);
                            }
                        }
                    } else {
                        vscode.window.showInformationMessage('Documentation generated successfully');

                        // Reload document
                        if (doc) {
                            const document = await vscode.workspace.openTextDocument(doc.uri);
                            await vscode.window.showTextDocument(document);
                        }
                    }

                    progress.report({ increment: 100 });
                } catch (error: any) {
                    vscode.window.showErrorMessage(`DocGenius error: ${error.message}`);
                    console.error('DocGenius error:', error);
                }
            }
        );
    } catch (error: any) {
        vscode.window.showErrorMessage(`DocGenius error: ${error.message}`);
        console.error('DocGenius error:', error);
    }
}

