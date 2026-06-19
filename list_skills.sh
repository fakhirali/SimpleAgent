#!/usr/bin/env bash
# List all skills from ~/.agents/skills with name, description, and path.

set -e

SKILLS_DIR="$HOME/.agents/skills"

if [[ ! -d "$SKILLS_DIR" ]]; then
  echo "[ERROR] $SKILLS_DIR not found"
  exit 1
fi

echo "═══════════════════════════════════════════════"
echo "  .agents/skills"
echo "═══════════════════════════════════════════════"

# Iterate over skill subdirectories
for skill in "$SKILLS_DIR"/*/; do
  [[ -d "$skill" ]] || continue
  skill="${skill%/}"  # remove trailing slash
  skill_name="$(basename "$skill")"
  sk_file="$skill/SKILL.md"

  if [[ ! -f "$sk_file" ]]; then
    echo "  • $skill_name  (no SKILL.md)"
    continue
  fi

  # Extract name: and description: from YAML frontmatter (between first two ---)
  name=$(sed -n '/^---$/,/^---$/p' "$sk_file" \
         | sed -n 's/^name:[[:space:]]*\(.*\)/\1/p' \
         | head -1)
  desc=$(sed -n '/^---$/,/^---$/p' "$sk_file" \
         | sed -n 's/^description:[[:space:]]*\(.*\)/\1/p' \
         | head -1)

  # Fallback: if no frontmatter name, use directory name
  [[ -z "$name" ]] && name="$skill_name"

  echo "  • $name"
  echo "    $desc"
  echo "    📄 $sk_file"
  echo
done
