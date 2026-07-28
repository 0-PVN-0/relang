package pipes;

import java.util.List;

public class PipeConfig {
    public int pipes = 1;
    public int fps = 75;
    public int steady = 13;
    public int limit = 2000;
    public boolean randomStart = false;
    public boolean bold = true;
    public boolean color = true;
    public boolean keepStyle = false;
    public List<Integer> colors = List.of(1, 2, 3, 4, 5, 6, 7, 0);
    public List<Integer> pipeTypes = List.of(0);
}
