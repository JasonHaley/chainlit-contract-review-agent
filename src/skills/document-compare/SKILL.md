---
name: document-compare
description: Compare two versions of a document (markdown or PDF) and display a summary of changes plus a git-style unified diff. Shows line counts for additions, deletions, and modifications. Use this skill whenever the user wants to see what changed between document versions, review revisions, compare contracts or handbooks, dentify edits, or find differences between two documents. Works with markdown files, plain text, or PDFs.
compatibility: Requires python3 and the difflib library
---

# Document Comparison Skill

Compare two versions of a document and display the differences using a git-style unified diff format, making it easy to see exactly what was added, removed, or modified.

## When to use this skill

- **Contract reviews**: Compare original and revised contract versions to see negotiated changes
- **Document updates**: Check what changed in employee handbooks, policies, or other reference docs
- **Version control**: Review differences between any two document versions
- **Change tracking**: Identify all additions, deletions, and modifications at a glance

## How it works

1. **Prepare your documents**: You can provide documents as:
   - Two separate uploaded files (markdown or PDF)
   - Two text blocks pasted in the conversation
   - A mix of both

2. **Run the comparison**: Claude will:
   - Extract or read the content from both documents
   - Perform a line-by-line comparison
   - Generate a unified diff showing all changes

3. **Read the output**: The diff uses standard git-style formatting:
   - `+` prefix = lines added in the new version
   - `-` prefix = lines removed from the old version
   - No prefix = context lines (unchanged)
   - `@@` markers show line numbers and location of changes

## Output format

The skill provides:

1. **Change Summary** (at the top)
   - Total lines added
   - Total lines removed
   - Total lines modified
   - Overall change percentage

2. **Unified Diff** (detailed view)
```
--- Original Document
+++ Updated Document
@@ -5,3 +5,4 @@ Section Header
 Unchanged line here
-Old text that was removed
+New text that was added
 Another unchanged line
```

The diff uses standard git conventions:
- `-` prefix = removed lines
- `+` prefix = added lines  
- No prefix = context (unchanged)
- `@@` = line numbers and change location

## Handling large documents

For very long documents, the output focuses on:
- Line numbers where changes occur
- Context surrounding each change (typically 3 lines before/after)
- A summary of total additions and deletions at the top

## Tips

- **PDFs**: Content is extracted as text, so formatting and layout may not be preserved in the comparison
- **Whitespace**: All whitespace differences are shown (including indentation changes)
- **Line endings**: Differences in line endings will be detected
- **Best results**: Works best when documents have clear line structure (not single-paragraph blobs)
