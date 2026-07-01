
if [ -n "$1" ]; then

sed -i "s/^version = \".*\"$/version = \"$1\"/" pyproject.toml

rm dist/*
uv sync
uv build
$(export UV_PUBLISH_TOKEN=$(cat token))

else
    echo "Missing version"

fi