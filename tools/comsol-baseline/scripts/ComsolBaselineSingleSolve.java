import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class ComsolBaselineSingleSolve {
  private static final double[][] SENSOR_POINTS = new double[][] {
    {27.7588406, -16.7032709, -143.970078},
    {45.3588409, -16.7013884, -143.977974},
    {62.9588432, -16.7015066, -143.977478},
    {80.5588379, -16.8233128, -143.949142}
  };

  private static final String[] SENSOR_NAMES = new String[] {"A", "B", "C", "N"};
  private static final String[] EXPRS = new String[] {"mf.Bx", "mf.By", "mf.Bz", "mf.normB"};
  private static final String[] UNITS = new String[] {"G", "G", "G", "G"};

  private static String join(String[] xs) {
    return xs == null ? "<null>" : Arrays.toString(xs);
  }

  public static void main(String[] args) throws Exception {
    if (args.length < 1) {
      throw new IllegalArgumentException("Usage: ComsolBaselineSingleSolve <input.mph> [dtDeg]");
    }
    String input = args[0];
    String dt = args.length >= 2 ? args[1] : "45";

    Model model = null;
    try {
      model = ModelUtil.loadCopy("BaselineSingleSolve", input);
      System.out.println("SINGLE_SOLVE_BEGIN");
      System.out.println("input=" + input);
      System.out.println("dt_requested=" + dt);

      try {
        StudyFeature param = model.study("std1").feature("param");
        System.out.println("param_before_pname=" + join(param.getStringArray("pname")));
        System.out.println("param_before_plistarr=" + join(param.getStringArray("plistarr")));
        param.set("pname", new String[] {"dt"});
        param.set("plistarr", new String[] {dt});
        param.set("punit", new String[] {""});
        System.out.println("param_after_pname=" + join(param.getStringArray("pname")));
        System.out.println("param_after_plistarr=" + join(param.getStringArray("plistarr")));
      } catch (Exception ex) {
        System.out.println("param_setup_status=failed");
        System.out.println("param_setup_error=" + ex.getClass().getName() + ": " + ex.getMessage());
        throw ex;
      }

      System.out.println("study_run_begin=std1");
      model.study("std1").run();
      System.out.println("study_run_status=success");

      System.out.println("SINGLE_SOLVE_CSV_BEGIN");
      System.out.println("sensor,dt_deg,Bx_G,By_G,Bz_G,normB_G");
      for (int i = 0; i < SENSOR_POINTS.length; i++) {
        String tag = "baseline_single_" + (i + 1);
        try { model.result().numerical().remove(tag); } catch (Exception ignore) {}
        model.result().numerical().create(tag, "Interp");
        model.result().numerical(tag).set("data", "dset4");
        model.result().numerical(tag).set("expr", EXPRS);
        model.result().numerical(tag).set("unit", UNITS);
        model.result().numerical(tag).set("coord", new double[][] {
          {SENSOR_POINTS[i][0]},
          {SENSOR_POINTS[i][1]},
          {SENSOR_POINTS[i][2]}
        });
        double[][] values = model.result().numerical(tag).getReal();
        System.out.printf(Locale.US, "%s,%s", SENSOR_NAMES[i], dt);
        for (int r = 0; r < values.length; r++) {
          for (int c = 0; c < values[r].length; c++) {
            System.out.printf(Locale.US, ",%.12g", values[r][c]);
          }
        }
        System.out.println();
      }
      System.out.println("SINGLE_SOLVE_CSV_END");
      System.out.println("single_solve_status=success");
      System.out.println("SINGLE_SOLVE_END");
    } catch (Exception ex) {
      System.out.println("single_solve_status=failed");
      System.out.println("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace();
      throw ex;
    } finally {
      try { if (model != null) ModelUtil.remove("BaselineSingleSolve"); } catch (Exception ignore) {}
    }
  }
}
