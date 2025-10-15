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
  const decorationOptions: { [key: string]: vscode.DecorationOptions[] } = {};

  feedback.forEach((f) => {
    const severity = f.severity || "medium";
    if (!decorations[severity]) {
      decorations[severity] = vscode.window.createTextEditorDecorationType({
        backgroundColor: severityColors[severity],
      });
      decorationOptions[severity] = [];
    }
    let lineNum = 0;
    if (f.line != null && f.line > 0 && f.line <= editor.document.lineCount) {
      lineNum = f.line - 1;
    }
    const range = new vscode.Range(
      lineNum,
      0,
      lineNum,
      editor.document.lineAt(lineNum).text.length
    );
    const hoverMessage = new vscode.MarkdownString(
      `**${severity.toUpperCase()}**: ${f.message}${
        f.reasoning ? `\n\n${f.reasoning}` : ""
      }`
    );
    decorationOptions[severity].push({ range, hoverMessage });
  });

  Object.keys(decorations).forEach((severity) => {
    editor.setDecorations(decorations[severity], decorationOptions[severity]);
  });
}
export function deactivate() {}
