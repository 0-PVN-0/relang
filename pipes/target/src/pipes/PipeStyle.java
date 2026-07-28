package pipes;

public enum PipeStyle {
    HEAVY(0),
    CURVED(1),
    LIGHT(2),
    DOUBLE(3),
    KNOBBY(4),
    ANGLES(5),
    DOTS(6),
    DOTS_O(7),
    SLASHES(8),
    MIXED(9);

    public final int value;

    PipeStyle(int value) {
        this.value = value;
    }

    public static PipeStyle fromInt(int v) {
        for (PipeStyle s : values()) {
            if (s.value == v) return s;
        }
        return HEAVY;
    }
}
