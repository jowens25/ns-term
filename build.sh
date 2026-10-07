
if [ -n "$1" ]; then

sed -i "s/^version = \".*\"$/version = \"$1\"/" pyproject.toml

rm dist/*
uv sync
uv build

./publish.sh

else
    echo "Missing version"

fi