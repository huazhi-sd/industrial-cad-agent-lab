import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class ComsolBaselineSensorEval {
  private static final double[][] SENSOR_POINTS = new double[][] {
    {27.7588406, -16.7032709, -143.970078},
    {45.3588409, -16.7013884, -143.977974},
    {62.9588432, -16.7015066, -143.977478},
    {80.5588379, -16.8233128, -143.949142}
  };

  private static final String[] SENSOR_NAMES = new String[] {"A", "B", "C", "N"};
  private static final String[] EXPRS = new String[] {"mf.Bx", "mf.By", "mf.Bz", "mf.normB"};
  private static final String[] UNITS = new String[] {"G", "G", "G", "G"};

  public static void main(String[] args) throws Exception {
    if (args.length < 1) {
      throw new IllegalArgumentException("Usage: ComsolBaselineSensorEval <input.mph> [datasetTag]");
    }
    String input = args[0];
    String dataset = args.length >= 2 ? args[1] : "dset4";

    Model model = null;
    try {
      model = ModelUtil.load("BaselineSensorEval", input);
      System.out.println("SENSOR_EVAL_BEGIN");
      System.out.println("input=" + input);
      System.out.println("dataset=" + dataset);
      System.out.println("exprs=" + Arrays.toString(EXPRS));
      System.out.println("units=" + Arrays.toString(UNITS));
      System.out.println("csv_header=sensor,dt_deg,Bx_G,By_G,Bz_G,normB_G");
      System.out.println("SENSOR_EVAL_CSV_BEGIN");
      System.out.println("sensor,dt_deg,Bx_G,By_G,Bz_G,normB_G");

      int[] solutionIndices = new int[] {1, 10, 19};
      for (int i = 0; i < SENSOR_POINTS.length; i++) {
        String tag = "baseline_eval_" + (i + 1);
        try { model.result().numerical().remove(tag); } catch (Exception ignore) {}
        model.result().numerical().create(tag, "Interp");
        model.result().numerical(tag).set("data", dataset);
        model.result().numerical(tag).set("expr", EXPRS);
        model.result().numerical(tag).set("unit", UNITS);
        model.result().numerical(tag).set("coord", new double[][] {
          {SENSOR_POINTS[i][0]},
          {SENSOR_POINTS[i][1]},
          {SENSOR_POINTS[i][2]}
        });

        for (int solIndex : solutionIndices) {
          double dt = (solIndex - 1) * 10.0;
          double[][] values = model.result().numerical(tag).getReal(false, solIndex);
          System.out.printf(Locale.US, "%s,%.0f", SENSOR_NAMES[i], dt);
          for (int r = 0; r < values.length; r++) {
            for (int c = 0; c < values[r].length; c++) {
              System.out.printf(Locale.US, ",%.12g", values[r][c]);
            }
          }
          System.out.println();
        }
      }

      System.out.println("SENSOR_EVAL_CSV_END");
      System.out.println("sensor_eval_status=success");
      System.out.println("SENSOR_EVAL_END");
    } catch (Exception ex) {
      System.out.println("sensor_eval_status=failed");
      System.out.println("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace();
      throw ex;
    } finally {
      try { if (model != null) ModelUtil.remove("BaselineSensorEval"); } catch (Exception ignore) {}
    }
  }
}
