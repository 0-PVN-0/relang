package pipes;

import java.util.*;

public class Renderer {
    private static final String[] PIPE_SETS = {
        "\u2503\u250F \u2513\u251B\u2501\u2513  \u2517\u2503\u251B\u2517 \u250F\u2501",
        "\u2502\u256D \u256E\u256F\u2500\u256E  \u2570\u2502\u256F\u2570 \u256D\u2500",
        "\u2502\u250C \u2510\u2518\u2500\u2510  \u2514\u2502\u2518\u2514 \u250C\u2500",
        "\u2551\u2554 \u2557\u255D\u2550\u2557  \u255A\u2551\u255D\u255A \u2554\u2550",
        "|+ ++-+  +|++ +-",
        "|/ \\ /-\\  \\|/\\ /",
        ".o ....  .... .o",
        ".o oo.o  o.oo o.",
        "-\\ /\\|/  /-\\/ \\|",
        "\u257F\u250D \u2511\u251A\u257C\u2512  \u2515\u257D\u2519\u2516 \u250E\u257E"
    };

    private final Terminal terminal;
    private final PipeConfig config;
    private final List<String> sets = new ArrayList<>();
    private final StringBuilder batch = new StringBuilder(4096);

    public Renderer(Terminal terminal, PipeConfig config) {
        this.terminal = terminal;
        this.config = config;
        prepareSets();
    }

    private void prepareSets() {
        for (String pipeSet : PIPE_SETS) {
            String padded = pipeSet + "                ";
            sets.add(padded.substring(0, 16));
        }
    }

    public void drawPipe(PipeData pipe, Direction oldDir, Direction newDir) {
        int index = pipe.pipeType * 16 + oldDir.value * 4 + newDir.value;
        String ch = getChar(index);
        int y = pipe.y;
        int x = pipe.x;

        batch.append("\033[").append(y + 1).append(';').append(x + 1).append('H');
        if (config.bold) {
            batch.append("\033[1m");
        }
        if (config.color) {
            batch.append("\033[").append(30 + (pipe.color % 8)).append('m');
        }
        batch.append(ch);
        batch.append("\033[0m");
    }

    private String getChar(int index) {
        int setIdx = index / 16;
        int charIdx = index % 16;
        if (setIdx >= sets.size()) return "?";
        return String.valueOf(sets.get(setIdx).charAt(charIdx));
    }

    public void clear() {
        terminal.clearScreen();
    }

    public void render() {
        System.out.print(batch);
        System.out.flush();
        batch.setLength(0);
    }
}
