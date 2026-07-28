package pipes;

public class PipeData {
    public int x;
    public int y;
    public Direction direction;
    public int pipeType;
    public int color;

    public PipeData(int x, int y, Direction direction, int pipeType, int color) {
        this.x = x;
        this.y = y;
        this.direction = direction;
        this.pipeType = pipeType;
        this.color = color;
    }
}
