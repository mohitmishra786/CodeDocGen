import * as vscode from 'vscode';
import { generateForFile } from './commands/generateDocs';
import { configureAI, showStatus } from './commands/configureAI';
import { DocGenStatusBar } from './ui/statusBar';

export function activate(context: vscode.ExtensionContext) {
    console.log('DocGenius extension is now active');

    // Initialize status bar
    const statusBar = new DocGenStatusBar();
    context.subscriptions.push(statusBar);

    // Register commands
    context.subscriptions.push(
        vscode.commands.registerCommand('docgenius.generateForFile', async () => {
            await generateForFile(context, 'file');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('docgenius.generateForSelection', async () => {
            await generateForFile(context, 'selection');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('docgenius.generateForWorkspace', async () => {
            await generateForFile(context, 'workspace');
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('docgenius.configureAI', async () => {
            await configureAI();
        })
    );

    context.subscriptions.push(
        vscode.commands.registerCommand('docgenius.showStatus', async () => {
            await showStatus();
        })
    );

    // Auto-generate on save if enabled
    context.subscriptions.push(
        vscode.workspace.onDidSaveTextDocument(async (document) => {
            const config = vscode.workspace.getConfiguration('docgenius');
            if (config.get('autoGenerateOnSave')) {
                await generateForFile(context, 'file', document);
            }
        })
    );

    // Update status bar
    statusBar.update();
}

export function deactivate() {
    console.log('DocGenius extension is now deactivated');
}

