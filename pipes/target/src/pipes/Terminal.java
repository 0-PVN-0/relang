package pipes;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.*;

public class Terminal {
    private int width = 80;
    private int height = 24;
    private final BlockingQueue<Integer> inputQueue = new LinkedBlockingQueue<>();
    private Thread inputThread;
    private volatile boolean running = true;
    private boolean rawMode = false;
    private boolean hasJNA = false;

    public Terminal() {
        setupConsoleEncoding();
        detectTerminalSize();
        setupRawMode();
        startInputReader();
        Runtime.getRuntime().addShutdownHook(new Thread(this::shutdown));
    }

    private void setupConsoleEncoding() {
        String os = System.getProperty("os.name").toLowerCase();
        if (os.contains("win")) {
            try {
                System.setOut(new PrintStream(
                    new BufferedOutputStream(new FileOutputStream(FileDescriptor.out), 8192),
                    true,
                    StandardCharsets.UTF_8
                ));
                try {
                    Class<?> kernel32Class = Class.forName("com.sun.jna.platform.win32.Kernel32");
                    Class<?> handleClass = Class.forName("com.sun.jna.platform.win32.WinNT$HANDLE");
                    java.lang.reflect.Field instanceField = kernel32Class.getField("INSTANCE");
                    Object kernel32 = instanceField.get(null);
                    java.lang.reflect.Method getStdHandle = kernel32Class.getMethod("GetStdHandle", int.class);
                    java.lang.reflect.Method setConsoleOutputCP = kernel32Class.getMethod("SetConsoleOutputCP", int.class);
                    Object outHandle = getStdHandle.invoke(kernel32, -11);
                    setConsoleOutputCP.invoke(kernel32, 65001);
                    java.lang.reflect.Method setConsoleCP = kernel32Class.getMethod("SetConsoleCP", int.class);
                    setConsoleCP.invoke(kernel32, 65001);
                } catch (Exception e) {
                    // JNA not available, but UTF-8 output stream is already set
                }
            } catch (Exception e) {
                // fall back to default encoding
            }
        }
    }

    private void detectTerminalSize() {
        String os = System.getProperty("os.name").toLowerCase();
        if (os.contains("win")) {
            if (!detectSizeJNA() || width < 10 || height < 4) {
                detectSizeModeCon();
            }
        } else {
            detectSizeStty();
        }
    }

    private boolean detectSizeJNA() {
        try {
            Class<?> kernel32Class = Class.forName("com.sun.jna.platform.win32.Kernel32");
            Class<?> handleClass = Class.forName("com.sun.jna.platform.win32.WinNT$HANDLE");
            Class<?> csbiClass = Class.forName("com.sun.jna.platform.win32.Wincon$CONSOLE_SCREEN_BUFFER_INFO");
            Class<?> smallRectClass = Class.forName("com.sun.jna.platform.win32.WinDef$SMALL_RECT");

            java.lang.reflect.Field instanceField = kernel32Class.getField("INSTANCE");
            Object kernel32 = instanceField.get(null);

            java.lang.reflect.Method getStdHandle = kernel32Class.getMethod("GetStdHandle", int.class);
            java.lang.reflect.Method getConsoleScreenBufferInfo = kernel32Class.getMethod(
                    "GetConsoleScreenBufferInfo", handleClass, csbiClass);

            Object outHandle = getStdHandle.invoke(kernel32, -11);
            Object bufferInfo = csbiClass.getDeclaredConstructor().newInstance();
            boolean ok = (boolean) getConsoleScreenBufferInfo.invoke(kernel32, outHandle, bufferInfo);

            if (ok) {
                Object srWindow = csbiClass.getField("srWindow").get(bufferInfo);
                short right = smallRectClass.getField("Right").getShort(srWindow);
                short left = smallRectClass.getField("Left").getShort(srWindow);
                short bottom = smallRectClass.getField("Bottom").getShort(srWindow);
                short top = smallRectClass.getField("Top").getShort(srWindow);
                width = right - left + 1;
                height = bottom - top + 1;
                return true;
            }
        } catch (Exception e) {
            // JNA not available or failed
        }
        return false;
    }

    private void detectSizeModeCon() {
        try {
            Process p = new ProcessBuilder("cmd", "/c", "mode", "con")
                    .redirectErrorStream(true).start();
            try (BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                String line;
                while ((line = r.readLine()) != null) {
                    String lc = line.toLowerCase();
                    if (lc.contains("lines")) {
                        String[] parts = lc.split(":");
                        if (parts.length > 1) {
                            int h = Integer.parseInt(parts[1].trim());
                            if (h > 0 && h < 200) height = h;
                            else height = Math.min(h, 80);
                        }
                    }
                    if (lc.contains("columns")) {
                        String[] parts = lc.split(":");
                        if (parts.length > 1) {
                            int w = Integer.parseInt(parts[1].trim());
                            if (w > 0 && w < 500) width = w;
                            else width = Math.min(w, 120);
                        }
                    }
                }
            }
            p.waitFor(1, TimeUnit.SECONDS);
        } catch (Exception e) {
            // keep defaults
        }
    }

    private void detectSizeStty() {
        try {
            Process p = new ProcessBuilder("sh", "-c", "stty size < /dev/tty")
                    .redirectErrorStream(true).start();
            try (BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()))) {
                String line = r.readLine();
                if (line != null) {
                    String[] parts = line.split("\\s+");
                    if (parts.length >= 2) {
                        int h = Integer.parseInt(parts[0]);
                        int w = Integer.parseInt(parts[1]);
                        if (h > 0) height = h;
                        if (w > 0) width = w;
                    }
                }
            }
            p.waitFor(1, TimeUnit.SECONDS);
        } catch (Exception e) {
            // keep defaults
        }
    }

    private void setupRawMode() {
        String os = System.getProperty("os.name").toLowerCase();
        try {
            if (os.contains("win")) {
                hasJNA = enableWindowsRawViaJNA();
            } else {
                Runtime.getRuntime().exec(new String[]{
                        "sh", "-c", "stty raw -echo < /dev/tty"
                });
                rawMode = true;
            }
        } catch (Exception e) {
            rawMode = false;
        }
    }

    private boolean enableWindowsRawViaJNA() {
        try {
            Class<?> kernel32Class = Class.forName("com.sun.jna.platform.win32.Kernel32");
            Class<?> handleClass = Class.forName("com.sun.jna.platform.win32.WinNT$HANDLE");

            java.lang.reflect.Field instanceField = kernel32Class.getField("INSTANCE");
            Object kernel32 = instanceField.get(null);

            java.lang.reflect.Method getStdHandle = kernel32Class.getMethod("GetStdHandle", int.class);
            java.lang.reflect.Method getConsoleMode = kernel32Class.getMethod("GetConsoleMode", handleClass, int[].class);
            java.lang.reflect.Method setConsoleMode = kernel32Class.getMethod("SetConsoleMode", handleClass, int.class);

            Object inHandle = getStdHandle.invoke(kernel32, -10);
            int[] inMode = new int[1];
            getConsoleMode.invoke(kernel32, inHandle, inMode);

            int newMode = inMode[0];
            newMode &= ~0x0002;
            newMode &= ~0x0004;
            newMode |= 0x0200;
            newMode |= 0x0080;
            setConsoleMode.invoke(kernel32, inHandle, newMode);

            Object outHandle = getStdHandle.invoke(kernel32, -11);
            int[] outMode = new int[1];
            getConsoleMode.invoke(kernel32, outHandle, outMode);
            setConsoleMode.invoke(kernel32, outHandle, outMode[0] | 0x0004);

            rawMode = true;
            return true;
        } catch (Exception e) {
            return false;
        }
    }

    private void startInputReader() {
        inputThread = new Thread(() -> {
            try {
                InputStream in = System.in;
                byte[] buf = new byte[1];
                while (running) {
                    int n = in.read(buf);
                    if (n > 0) {
                        inputQueue.offer((int) buf[0] & 0xFF);
                    }
                }
            } catch (IOException e) {
                // thread ends
            }
        });
        inputThread.setDaemon(true);
        inputThread.start();
    }

    public int readKey() {
        Integer key = inputQueue.poll();
        return key != null ? key : -1;
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public boolean checkResize() {
        int oldW = width, oldH = height;
        detectTerminalSize();
        return width != oldW || height != oldH;
    }

    public void hideCursor() {
        System.out.print("\033[?25l");
    }

    public void showCursor() {
        System.out.print("\033[?25h");
    }

    public void clearScreen() {
        System.out.print("\033[2J\033[H");
    }

    public void printAt(int y, int x, String s, int colorIndex, boolean useColor, boolean useBold) {
        System.out.print("\033[" + (y + 1) + ";" + (x + 1) + "H");
        if (useBold) {
            System.out.print("\033[1m");
        }
        if (useColor) {
            int ansiColor = 30 + (colorIndex % 8);
            System.out.print("\033[" + ansiColor + "m");
        }
        System.out.print(s);
        System.out.print("\033[0m");
    }

    public void flush() {
        System.out.flush();
    }

    public void shutdown() {
        running = false;
        showCursor();
        clearScreen();
        flush();
        String os = System.getProperty("os.name").toLowerCase();
        if (!os.contains("win")) {
            try {
                Runtime.getRuntime().exec(new String[]{
                        "sh", "-c", "stty sane < /dev/tty"
                });
            } catch (Exception e) {
                // ignore
            }
        }
        if (inputThread != null) {
            try {
                inputThread.join(500);
            } catch (InterruptedException e) {
                // ignore
            }
        }
    }
}
