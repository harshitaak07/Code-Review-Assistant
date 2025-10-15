import * as vscode from "vscode";
import { submitCode, getFeedback } from "./api";

export function activate(context: vscode.ExtensionContext) {
  console.log("Code Review Assistant activated");

  let disposable = vscode.commands.registerCommand(
    "codeReviewAssistant.reviewCode",
    async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) return;

      const code = editor.document.getText();
      const submissionId = await submitCode(code);
      vscode.window.showInformationMessage(
        `Code submitted for review (ID: ${submissionId})`
      );

      const feedback = await getFeedback(submissionId);
      highlightFeedback(editor, feedback);
    }
  );

  context.subscriptions.push(disposable);
  vscode.workspace.onDidSaveTextDocument(
    async (document: vscode.TextDocument) => {
      const editor = vscode.window.activeTextEditor;
      if (!editor || editor.document !== document) return;

      const code = document.getText();
      const submissionId = await submitCode(code);
      const feedback = await getFeedback(submissionId);
      highlightFeedback(editor, feedback);
    }
  );
}

function highlightFeedback(editor: vscode.TextEditor, feedback: any[]) {
  const severityColors: { [key: string]: string } = {
    high: "rgba(255,0,0,0.3)",
    medium: "rgba(255,255,0,0.3)",
    low: "rgba(0,0,255,0.3)",
  };

  const decorations: { [key: string]: vscode.TextEditorDecorationType } = {};

  for (const f of feedback) {
    const severity = f.severity || "medium";
    if (!decorations[severity]) {
      decorations[severity] = vscode.window.createTextEditorDecorationType({
        backgroundColor: severityColors[severity],
      });
    }
  }

  for (const severity of Object.keys(decorations)) {
    const ranges: vscode.Range[] = feedback
      .filter((f) => f.severity === severity)
      .map((f) => {
        const line = Math.max((f.line || 1) - 1, 0);
        return new vscode.Range(
          line,
          0,
          line,
          editor.document.lineAt(line).text.length
        );
      });
    editor.setDecorations(decorations[severity], ranges);
  }
}

export function deactivate() {}
