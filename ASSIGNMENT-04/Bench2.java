import java.lang.management.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.nio.file.*;

/** Task 2 (Part II): single-thread vs multi-thread on the same JVM, with CPU time, context switches, heap and latency. */
public class Bench2 {
    static final ThreadMXBean TM = ManagementFactory.getThreadMXBean();
    static long ctxSwitches() {            // voluntary + involuntary, whole process
        long v = 0;
        try { for (String l : Files.readAllLines(Paths.get("/proc/self/status")))
            if (l.startsWith("voluntary_ctxt_switches") || l.startsWith("nonvoluntary_ctxt_switches")) v += Long.parseLong(l.split("\\s+")[1]);
        } catch (Exception e) {}
        return v;
    }
    static long allThreadsCpu() { long s = 0; for (long id : TM.getAllThreadIds()) { long c = TM.getThreadCpuTime(id); if (c > 0) s += c; } return s; }
    static long usedHeap() { Runtime r = Runtime.getRuntime(); return r.totalMemory() - r.freeMemory(); }

    // ---- workload 1: box blur over an image (rows are independent) ----
    static int W = 1600, H = 1600;
    static int[] img = new int[W * H], out = new int[W * H];
    static void blurRows(int r0, int r1) {
        for (int y = r0; y < r1; y++) for (int x = 0; x < W; x++) {
            int s = 0, n = 0;
            for (int dy = -2; dy <= 2; dy++) for (int dx = -2; dx <= 2; dx++) {
                int yy = y + dy, xx = x + dx; if (yy < 0 || yy >= H || xx < 0 || xx >= W) continue; s += img[yy * W + xx]; n++; }
            out[y * W + x] = s / n;
        }
    }
    static void blurSingle() { blurRows(0, H); }
    static void blurMulti(int threads) throws Exception {
        ExecutorService ex = Executors.newFixedThreadPool(threads); List<Future<?>> fs = new ArrayList<>();
        int chunk = H / threads; for (int t = 0; t < threads; t++) { final int a = t * chunk, b = (t == threads - 1) ? H : a + chunk; fs.add(ex.submit(() -> blurRows(a, b))); }
        for (Future<?> f : fs) f.get(); ex.shutdown();
    }
    // ---- workload 2: tiny task (sum of 200 numbers) repeated 2000 times, new thread per task ----
    static long tinySum(int[] a) { long s = 0; for (int v : a) s += v; return s; }
    static volatile long SINK; static void tinySingle(int reps) { int[] a = new int[200]; for (int i = 0; i < 200; i++) a[i] = i; long s = 0; for (int r = 0; r < reps; r++) { a[r % 200] = r; s += tinySum(a); } SINK = s; }
    static void tinyMulti(int reps) throws Exception { int[] a = new int[200]; for (int i = 0; i < 200; i++) a[i] = i; List<Thread> ts = new ArrayList<>();
        AtomicLong s = new AtomicLong(); for (int r = 0; r < reps; r++) { a[r % 200] = r; Thread t = new Thread(() -> s.addAndGet(tinySum(a))); t.start(); ts.add(t); if (ts.size() == 50) { for (Thread x : ts) x.join(); ts.clear(); } } for (Thread x : ts) x.join(); }
    // ---- workload 3: lock-contended counter ----
    static long shared = 0; static final Object LOCK = new Object();
    static void contendSingle(int n) { shared = 0; for (int i = 0; i < n; i++) synchronized (LOCK) { shared++; } }
    static void contendMulti(int n, int threads) throws Exception { shared = 0; Thread[] ts = new Thread[threads];
        for (int t = 0; t < threads; t++) { ts[t] = new Thread(() -> { for (int i = 0; i < n / threads; i++) synchronized (LOCK) { shared++; } }); ts[t].start(); } for (Thread t : ts) t.join(); }

    interface Job { void run() throws Exception; }
    static long procCpuTicks() { try { String[] f = Files.readAllLines(Paths.get("/proc/self/stat")).get(0).split("\\)")[1].trim().split("\\s+"); return Long.parseLong(f[11]) + Long.parseLong(f[12]); } catch (Exception e) { return -1; } }
    public static void main(String[] a) throws Exception {
        String sc = a[0]; int reps = Integer.parseInt(a[1]);
        Random rnd = new Random(1); for (int i = 0; i < img.length; i++) img[i] = rnd.nextInt(256);
        Job j;
        switch (sc) {
            case "blur1": j = Bench2::blurSingle; break;
            case "blur2": j = () -> blurMulti(2); break;
            case "blur8": j = () -> blurMulti(8); break;
            case "tiny1": j = () -> tinySingle(2000); break;
            case "tinyN": j = () -> tinyMulti(2000); break;
            case "cont1": j = () -> contendSingle(4_000_000); break;
            case "cont4": j = () -> contendMulti(4_000_000, 4); break;
            default: return;
        }
        for (int i = 0; i < 5; i++) j.run();                  // warm-up so that the JIT has compiled the hot code
        double[] ms = new double[reps]; long c0 = procCpuTicks();
        long a0 = ((com.sun.management.ThreadMXBean) TM).getThreadAllocatedBytes(Thread.currentThread().getId());
        for (int i = 0; i < reps; i++) { long t0 = System.nanoTime(); j.run(); ms[i] = (System.nanoTime() - t0) / 1e6; }
        long c1 = procCpuTicks();
        Arrays.sort(ms); double mean = Arrays.stream(ms).average().getAsDouble();
        System.out.printf(Locale.ROOT, "%s|mean_ms=%.2f|p50=%.2f|worst=%.2f|cpu_ms_per_run=%.1f|heapMB=%.1f|threads_peak=%d%n", sc, mean, ms[reps/2], ms[reps-1], (c1 - c0) * 10.0 / reps, usedHeap() / 1e6, TM.getPeakThreadCount());
    }
}
