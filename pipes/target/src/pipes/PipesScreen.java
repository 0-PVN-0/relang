package pipes;

import java.util.*;

public class PipesScreen {
    private final Terminal terminal;
    private final PipeConfig config;
    private final Renderer renderer;
    private final List<PipeData> pipes = new ArrayList<>();
    private final Random random = new Random();
    private int count;
    private double delay;

    public PipesScreen(Terminal terminal, PipeConfig config) {
        this.terminal = terminal;
        this.config = config;
        this.renderer = new Renderer(terminal, config);
        this.delay = 1.0 / config.fps;
        initPipes();
    }

    private void initPipes() {
        for (int i = 0; i < config.pipes; i++) {
            Direction dir;
            int x, y;
            if (config.randomStart) {
                dir = Direction.fromInt(random.nextInt(4));
                x = random.nextInt(terminal.getWidth());
                y = random.nextInt(terminal.getHeight());
            } else {
                dir = Direction.UP;
                x = terminal.getWidth() / 2;
                y = terminal.getHeight() / 2;
            }
            int pipeType = config.pipeTypes.get(random.nextInt(config.pipeTypes.size()));
            int color = config.colors.get(random.nextInt(config.colors.size()));
            pipes.add(new PipeData(x, y, dir, pipeType, color));
        }
    }

    public boolean update() {
        int key = terminal.readKey();
        if (key != -1 && !handleKey(key)) {
            return false;
        }

        if (terminal.checkResize()) {
            renderer.clear();
        }

        updatePipes();
        renderer.render();

        count += pipes.size();
        if (config.limit > 0 && count >= config.limit) {
            renderer.clear();
            count = 0;
        }

        try {
            Thread.sleep((long) (delay * 1000));
        } catch (InterruptedException e) {
            return false;
        }
        return true;
    }

    private void updatePipes() {
        int h = terminal.getHeight();
        int w = terminal.getWidth();
        if (h <= 0 || w <= 0) return;

        for (PipeData pipe : pipes) {
            int x = pipe.x;
            int y = pipe.y;
            Direction oldDir = pipe.direction;

            if (oldDir.value % 2 == 1) {
                x += -oldDir.value + 2;
            } else {
                y += oldDir.value - 1;
            }

            if (x < 0 || x >= w || y < 0 || y >= h) {
                if (!config.keepStyle) {
                    pipe.pipeType = config.pipeTypes.get(random.nextInt(config.pipeTypes.size()));
                    pipe.color = config.colors.get(random.nextInt(config.colors.size()));
                }
                x = Math.floorMod(x, w);
                y = Math.floorMod(y, h);
            }

            Direction newDir = oldDir;
            if (config.steady > 0 && random.nextInt(config.steady) <= 1) {
                int turn = 2 * random.nextInt(2) - 1;
                newDir = Direction.fromInt((oldDir.value + turn + 4) % 4);
            }

            renderer.drawPipe(pipe, oldDir, newDir);

            pipe.x = x;
            pipe.y = y;
            pipe.direction = newDir;
        }
    }

    private boolean handleKey(int key) {
        char keyChar = 0;
        if (key >= 0 && key <= 255) {
            keyChar = Character.toUpperCase((char) key);
        }

        if (keyChar == 'P' && config.steady < 15) {
            config.steady++;
        } else if (keyChar == 'O' && config.steady > 3) {
            config.steady--;
            if (config.steady < 0) config.steady = 0;
        } else if (keyChar == 'F' && config.fps < 100) {
            config.fps++;
            delay = 1.0 / config.fps;
        } else if (keyChar == 'D' && config.fps > 20) {
            config.fps--;
            delay = 1.0 / config.fps;
        } else if (keyChar == 'B') {
            config.bold = !config.bold;
        } else if (keyChar == 'C') {
            config.color = !config.color;
        } else if (keyChar == 'K') {
            config.keepStyle = !config.keepStyle;
        } else if (keyChar == '?' || key == 27) {
            return false;
        }
        return true;
    }
}
