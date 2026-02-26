#!/bin/bash
# OdinOS GitHub Push Helper

# 1️⃣ Identity
git config --global user.name "odxnojEz"
git config --global user.email "ezimovagulnare86@gmail.com"

# 2️⃣ Embedded repos varsa, çıxar
git rm --cached -r models/no-cost-ai 2>/dev/null
git rm --cached -r odinos_core 2>/dev/null

# 3️⃣ Remote origin düzəlt
git remote remove origin 2>/dev/null
git remote add origin https://github.com/odxnojEz/OdinOS.git

# 4️⃣ Add & commit
git add .
git commit -m "Initial OdinOS commit — renamed from Acronix"

# 5️⃣ Push (token tələb olunur)
echo "⚠️ GitHub Personal Access Token tələb olunur."
echo "Username: odxnojEz"
echo "Password (token) daxil edin:"
git push -u origin main
