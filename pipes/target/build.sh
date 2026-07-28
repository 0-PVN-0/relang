#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
SRC="$DIR/src"
OUT="$DIR/out"
LIB="$DIR/lib"
JNA_VER="5.14.0"

mkdir -p "$OUT" "$LIB"

JNA_JAR="$LIB/jna-$JNA_VER.jar"
JNA_PLATFORM_JAR="$LIB/jna-platform-$JNA_VER.jar"

download_if_missing() {
    local url="$1"
    local dest="$2"
    if [ ! -f "$dest" ]; then
        echo "Downloading $(basename "$dest")..."
        if command -v curl >/dev/null 2>&1; then
            curl -sL "$url" -o "$dest" || return 1
        elif command -v wget >/dev/null 2>&1; then
            wget -q "$url" -O "$dest" || return 1
        else
            return 1
        fi
    fi
}

download_if_missing \
    "https://repo1.maven.org/maven2/net/java/dev/jna/jna/$JNA_VER/jna-$JNA_VER.jar" \
    "$JNA_JAR" || echo "Warning: Could not download JNA (non-critical)"

download_if_missing \
    "https://repo1.maven.org/maven2/net/java/dev/jna/jna-platform/$JNA_VER/jna-platform-$JNA_VER.jar" \
    "$JNA_PLATFORM_JAR" || echo "Warning: Could not download JNA Platform (non-critical)"

CP="$OUT"
[ -f "$JNA_JAR" ] && CP="$CP:$JNA_JAR"
[ -f "$JNA_PLATFORM_JAR" ] && CP="$CP:$JNA_PLATFORM_JAR"

find "$SRC" -name "*.java" > "$DIR/sources.txt"
javac -d "$OUT" -cp "$CP" @"$DIR/sources.txt"
rm -f "$DIR/sources.txt"

echo "Build successful."
echo "To run: $DIR/run.sh [options]"
