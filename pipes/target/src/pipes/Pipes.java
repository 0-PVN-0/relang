package pipes;

public class Pipes {
    private static final String VERSION = "2.0.0";

    public static void main(String[] args) {
        PipeConfig config = new PipeConfig();
        boolean saveConfig = false;

        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "-p":
                case "--pipes":
                    if (i + 1 < args.length) config.pipes = Math.max(1, Integer.parseInt(args[++i]));
                    break;
                case "-f":
                case "--fps":
                    if (i + 1 < args.length) config.fps = Math.max(20, Math.min(100, Integer.parseInt(args[++i])));
                    break;
                case "-s":
                case "--steady":
                    if (i + 1 < args.length) config.steady = Math.max(5, Math.min(15, Integer.parseInt(args[++i])));
                    break;
                case "-r":
                case "--limit":
                    if (i + 1 < args.length) config.limit = Math.max(0, Integer.parseInt(args[++i]));
                    break;
                case "-R":
                case "--random":
                    config.randomStart = true;
                    break;
                case "-B":
                case "--no-bold":
                    config.bold = false;
                    break;
                case "-C":
                case "--no-color":
                    config.color = false;
                    break;
                case "-P":
                case "--pipe-style":
                    if (i + 1 < args.length) {
                        int style = Integer.parseInt(args[++i]);
                        if (style >= 0 && style <= 9) {
                            config.pipeTypes = java.util.List.of(style);
                        }
                    }
                    break;
                case "-K":
                case "--keep-style":
                    config.keepStyle = true;
                    break;
                case "-S":
                case "--save-config":
                    saveConfig = true;
                    break;
                case "-v":
                case "--version":
                    System.out.println("pipes-java v" + VERSION);
                    return;
                case "-h":
                case "--help":
                    printHelp();
                    return;
            }
        }

        Terminal terminal = new Terminal();
        try {
            terminal.hideCursor();
            terminal.clearScreen();
            PipesScreen screen = new PipesScreen(terminal, config);
            while (screen.update()) {
                // loop
            }
        } catch (Exception e) {
            // exit cleanly
        } finally {
            terminal.clearScreen();
            terminal.showCursor();
            terminal.shutdown();
        }
    }

    private static void printHelp() {
        System.out.println("Usage: pipes-java [options]");
        System.out.println("Animated pipes terminal screensaver.");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  -p, --pipes N         number of pipes (default: 1)");
        System.out.println("  -f, --fps N           frames per second, 20-100 (default: 75)");
        System.out.println("  -s, --steady N        steadiness, 5-15 (default: 13)");
        System.out.println("  -r, --limit N         character limit before screen reset");
        System.out.println("  -R, --random          start pipes at random positions");
        System.out.println("  -B, --no-bold         disable bold characters");
        System.out.println("  -C, --no-color        disable colors");
        System.out.println("  -P N                  pipe style 0-9 (default: 0)");
        System.out.println("  -K, --keep-style      keep pipe style when wrapping");
        System.out.println("  -S, --save-config     save current settings (not implemented)");
        System.out.println("  -v, --version         show version");
        System.out.println();
        System.out.println("Interactive keys: O/P (steadiness), D/F (fps),");
        System.out.println("  B (bold), C (color), K (keep style), ?/ESC (quit)");
    }
}
