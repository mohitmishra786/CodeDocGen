import * as vscode from 'vscode';

export class DocGenStatusBar {
    private statusBarItem: vscode.StatusBarItem;

    constructor() {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'docgenius.showStatus';
        this.statusBarItem.show();
    }

    public update() {
        const config = vscode.workspace.getConfiguration('docgenius');
        const aiEnabled = config.get<boolean>('ai.enabled', false);
        const aiProvider = config.get<string>('ai.provider', 'nltk');

        if (aiEnabled) {
            this.statusBarItem.text = `$(file-code) DocGenius: ${aiProvider}`;
            this.statusBarItem.tooltip = `AI Provider: ${aiProvider} (Click for details)`;
        } else {
            this.statusBarItem.text = `$(file-code) DocGenius: NLTK`;
            this.statusBarItem.tooltip = 'Using NLTK analysis (Click for details)';
        }
    }

    public dispose() {
        this.statusBarItem.dispose();
    }
}

