import difflib
import sys


def generate_diff_with_stats(original_text, updated_text, original_name=\"Original\", updated_name=\"Updated\"):
    \"\"\"Generate a unified diff with statistics.\"\"\"
    
    original_lines = original_text.splitlines(keepends=True)
    updated_lines = updated_text.splitlines(keepends=True)
    
    # Generate the diff
    diff_lines = list(difflib.unified_diff(
        original_lines,
        updated_lines,
        fromfile=original_name,
        tofile=updated_name,
        lineterm=''
    ))
    
    # Calculate statistics
    additions = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
    deletions = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
    
    total_lines = len(original_lines)
    changes_pct = ((additions + deletions) / (total_lines * 2)) * 100 if total_lines > 0 else 0
    
    # Format output
    output = []
    output.append(\"=\" * 60)
    output.append(\"CHANGE SUMMARY\")
    output.append(\"=\" * 60)
    output.append(f\"Lines added:     {additions}\")
    output.append(f\"Lines removed:   {deletions}\")
    output.append(f\"Lines changed:   {additions + deletions}\")
    output.append(f\"Overall impact:  {changes_pct:.1f}%\")
    output.append(\"=\" * 60)
    output.append(\"\")
    output.extend('\
'.join(diff_lines).split('\
'))
    
    return '\
'.join(output)


if __name__ == \"__main__\":
    if len(sys.argv) < 3:
        print(\"Usage: python3 generate_diff_stats.py original.txt updated.txt\")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        original = f.read()
    
    with open(sys.argv[2], 'r') as f:
        updated = f.read()
    
    print(generate_diff_with_stats(original, updated, sys.argv[1], sys.argv[2]))
