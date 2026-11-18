import java.lang.management.*;
import java.util.*;
import javax.management.*;
import javax.management.openmbean.CompositeData;

/** Task 3 (Part II): runtime behaviour benchmark on the JVM (analogue of ART's interpreter / JIT tiers and GC). */
public class RuntimeBench {
    static volatile long SINK;
    // (i) CPU-bound: count primes below n with trial division
    static int cpu(int n) { int c = 0; for (int i = 2; i < n; i++) { boolean p = true; for (int d = 2; (long) d * d <= i; d++) if (i % d == 0) { p = false; break; } if (p) c++; } return c; }
    // (ii) allocation-heavy: build and drop many small objects and strings
    static int alloc(int n) { List<String> l = new ArrayList<>(); for (int i = 0; i < n; i++) { l.add("rec-" + i + "-" + (i * 31 % 97)); if (l.size() > 2000) l.clear(); } return l.size(); }
    // (iii) list rendering: bind 5000 rows of a view-model (format strings, compute layout width)
    static class Row { String title, subtitle; int w; }
    static int list(int rows) { Row[] rs = new Row[rows]; int total = 0; for (int i = 0; i < rows; i++) { Row r = new Row(); r.title = String.format("Order #%05d", i); r.subtitle = "Customer " + (i % 113) + " - " + (i * 7 % 1000) + " km"; r.w = r.title.length() * 9 + r.subtitle.length() * 7; rs[i] = r; total += r.w; } return total; }
    interface W { long run(); }
    static void gcStats(String tag) {
        long cnt = 0, ms = 0; for (GarbageCollectorMXBean g : ManagementFactory.getGarbageCollectorMXBeans()) { cnt += g.getCollectionCount(); ms += g.getCollectionTime(); }
        MemoryUsage mu = ManagementFactory.getMemoryMXBean().getHeapMemoryUsage();
        System.out.printf(Locale.ROOT, "GC|%s|collections=%d|total_pause_ms=%d|heap_used_MB=%.1f|heap_committed_MB=%.1f%n", tag, cnt, ms, mu.getUsed() / 1e6, mu.getCommitted() / 1e6);
    }
    static void bench() {
        String[] names = {"cpu", "alloc", "list"}; W[] ws = { () -> cpu(120000), () -> alloc(300000), () -> list(5000) };
        long t0 = System.nanoTime();
        for (int w = 0; w < 3; w++) {
            double first = 0, last = 0, sum = 0; int N = 12; double[] ms = new double[N];
            for (int i = 0; i < N; i++) { long a = System.nanoTime(); SINK += ws[w].run(); ms[i] = (System.nanoTime() - a) / 1e6; }
            double steady = 0; for (int i = N - 5; i < N; i++) steady += ms[i]; steady /= 5;
            System.out.printf(Locale.ROOT, "WL|%s|first_ms=%.1f|steady_ms=%.1f|cold_over_steady=%.1f%n", names[w], ms[0], steady, ms[0] / steady);
        }
        System.out.printf(Locale.ROOT, "TOTAL|ms=%.0f%n", (System.nanoTime() - t0) / 1e6);
        gcStats("bench");
        Runtime r = Runtime.getRuntime(); System.out.printf(Locale.ROOT, "HEAP|max_MB=%d%n", r.maxMemory() >> 20);
    }
    static final List<byte[]> LEAK = new ArrayList<>();
    static void leak() {
        MemoryPoolMXBean old = null; for (MemoryPoolMXBean p : ManagementFactory.getMemoryPoolMXBeans()) if (p.getType() == MemoryType.HEAP && p.isUsageThresholdSupported() && (p.getName().contains("Old") || p.getName().contains("Tenured"))) old = p;
        final long[] alarmAt = {-1}; long start = System.nanoTime();
        if (old != null) { old.setCollectionUsageThreshold((long) (old.getUsage().getMax() * 0.7));
            NotificationEmitter em = (NotificationEmitter) ManagementFactory.getMemoryMXBean();
            em.addNotificationListener((n, h) -> { if (alarmAt[0] < 0) alarmAt[0] = (System.nanoTime() - start) / 1_000_000; }, null, null); }
        int step = 0; long[] samples = new long[40];
        try { while (true) { LEAK.add(new byte[256 * 1024]); step++; if (step % 20 == 0 && step / 20 < samples.length) { System.gc(); samples[step / 20] = Runtime.getRuntime().totalMemory() - Runtime.getRuntime().freeMemory(); } } }
        catch (OutOfMemoryError e) { LEAK.clear(); System.out.printf(Locale.ROOT, "LEAK|OutOfMemoryError after %d allocations (%.0f MB leaked)|first_collection_threshold_alarm_ms=%d%n", step, step * 0.25, alarmAt[0]);
            StringBuilder sb = new StringBuilder("LEAKTREND|heap_after_gc_MB:"); for (int i = 1; i < samples.length && samples[i] > 0; i++) sb.append(String.format(Locale.ROOT, " %.0f", samples[i] / 1e6)); System.out.println(sb); }
    }
    static volatile long heartbeat = System.nanoTime();
    static void block() throws Exception {
        Thread dog = new Thread(() -> { long worst = 0; boolean reported = false; while (true) { try { Thread.sleep(100); } catch (InterruptedException e) { return; }
            long stall = (System.nanoTime() - heartbeat) / 1_000_000; worst = Math.max(worst, stall);
            if (stall > 500 && !reported) { reported = true; System.out.printf(Locale.ROOT, "WATCHDOG|main loop stalled %d ms (> 500 ms budget): reporting 'ANR-like' event with stack trace%n", stall); StackTraceElement[] st = Thread.getAllStackTraces().entrySet().stream().filter(e -> e.getKey().getName().equals("main")).findFirst().get().getValue(); System.out.println("WATCHDOG|main stack top: " + st[0] + " <- " + st[1]); } } });
        dog.setDaemon(true); dog.start();
        for (int frame = 0; frame < 40; frame++) { heartbeat = System.nanoTime(); if (frame == 20) { Thread.sleep(1500); /* blocking call on the main (UI) thread, e.g. synchronous network or disk */ } else Thread.sleep(16); }
        System.out.println("BLOCK|done");
    }
    public static void main(String[] a) throws Exception {
        switch (a[0]) { case "bench": bench(); break; case "leak": leak(); break; case "block": block(); break; }
    }
}
