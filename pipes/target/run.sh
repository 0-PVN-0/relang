#!/usr/bin/env bash
DIR="$(cd "$(dirname "$0")" && pwd)"
OUT="$DIR/out"
LIB="$DIR/lib"

if [ ! -d "$OUT" ]; then
    echo "Build directory not found. Run build.sh first."
    exit 1
fi

CP="$OUT"
[ -f "$LIB/jna-5.14.0.jar" ] && CP="$CP:$LIB/jna-5.14.0.jar"
[ -f "$LIB/jna-platform-5.14.0.jar" ] && CP="$CP:$LIB/jna-platform-5.14.0.jar"

exec java -cp "$CP" pipes.Pipes "$@"
