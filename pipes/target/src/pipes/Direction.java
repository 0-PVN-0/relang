package pipes;

public enum Direction {
    UP(0),
    RIGHT(1),
    DOWN(2),
    LEFT(3);

    public final int value;

    Direction(int value) {
        this.value = value;
    }

    public static Direction fromInt(int v) {
        for (Direction d : values()) {
            if (d.value == v) return d;
        }
        return UP;
    }
}
