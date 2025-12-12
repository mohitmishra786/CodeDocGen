import * as vscode from 'vscode';

export async function configureAI() {
    const config = vscode.workspace.getConfiguration('docgenius');

    const provider = await vscode.window.showQuickPick(
        [
            { label: 'NLTK (Local, No API Key)', value: 'nltk' },
            { label: 'Groq', value: 'groq' },
            { label: 'OpenAI', value: 'openai' },
            { label: 'Azure OpenAI', value: 'azure_openai' }
        ],
        { placeHolder: 'Select AI provider' }
    );

    if (!provider) {
        return;
    }

    await config.update('ai.provider', provider.value, vscode.ConfigurationTarget.Global);

    if (provider.value !== 'nltk') {
        const enable = await vscode.window.showQuickPick(
            ['Yes', 'No'],
            { placeHolder: 'Enable AI-powered documentation?' }
        );

        if (enable === 'Yes') {
            await config.update('ai.enabled', true, vscode.ConfigurationTarget.Global);

            if (provider.value === 'azure_openai') {
                // Configure Azure
                const authMethod = await vscode.window.showQuickPick(
                    [
                        { label: 'Azure CLI (az login)', value: 'azureCli' },
                        { label: 'API Key', value: 'apiKey' },
                        { label: 'Managed Identity', value: 'managedIdentity' }
                    ],
                    { placeHolder: 'Select authentication method' }
                );

                if (authMethod) {
                    await config.update('azure.authMethod', authMethod.value, vscode.ConfigurationTarget.Global);

                    if (authMethod.value === 'apiKey') {
                        const endpoint = await vscode.window.showInputBox({
                            prompt: 'Enter Azure OpenAI endpoint',
                            placeHolder: 'https://your-resource.openai.azure.com/'
                        });

                        if (endpoint) {
                            await config.update('azure.endpoint', endpoint, vscode.ConfigurationTarget.Global);
                        }

                        const deploymentName = await vscode.window.showInputBox({
                            prompt: 'Enter deployment name',
                            placeHolder: 'gpt-4',
                            value: 'gpt-4'
                        });

                        if (deploymentName) {
                            await config.update('azure.deploymentName', deploymentName, vscode.ConfigurationTarget.Global);
                        }
                    }
                }
            }

            vscode.window.showInformationMessage(`AI provider configured: ${provider.label}`);
        }
    } else {
        await config.update('ai.enabled', false, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('Using NLTK (local analysis, no API key required)');
    }
}

export async function showStatus() {
    const config = vscode.workspace.getConfiguration('docgenius');
    const aiEnabled = config.get<boolean>('ai.enabled', false);
    const aiProvider = config.get<string>('ai.provider', 'nltk');
    const azureAuthMethod = config.get<string>('azure.authMethod', 'azureCli');

    let statusMessage = `DocGenius Status\n\n`;
    statusMessage += `AI Enabled: ${aiEnabled ? 'Yes' : 'No'}\n`;
    statusMessage += `AI Provider: ${aiProvider}\n`;

    if (aiProvider === 'azure_openai') {
        statusMessage += `Azure Auth: ${azureAuthMethod}\n`;
    }

    statusMessage += `\nSupported Languages:\n`;
    statusMessage += `- Python\n`;
    statusMessage += `- C/C++\n`;
    statusMessage += `- Java\n`;
    statusMessage += `- JavaScript/TypeScript\n`;

    vscode.window.showInformationMessage(statusMessage, { modal: true });
}

