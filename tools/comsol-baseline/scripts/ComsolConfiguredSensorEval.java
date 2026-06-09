import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class ComsolConfiguredSensorEval {
  private static String[] splitList(String raw) {
    if (raw == null || raw.trim().isEmpty()) return new String[0];
    String[] items = raw.split(",");
    for (int i = 0; i < items.length; i++) items[i] = items[i].trim();
    return items;
  }

  private static int[] parseIntList(String raw) {
    String[] parts = splitList(raw);
    int[] values = new int[parts.length];
    for (int i = 0; i < parts.length; i++) values[i] = Integer.parseInt(parts[i]);
    return values;
  }

  private static void readSensorsInline(String raw, List<String> names, List<double[]> coords) {
    String[] rows = raw.split(";");
    for (int i = 0; i < rows.length; i++) {
      String row = rows[i].trim();
      if (row.isEmpty()) continue;
      String[] cells = row.split("\\|");
      if (cells.length < 4) {
        throw new IllegalArgumentException("Invalid inline sensor row " + (i + 1) + ": " + row);
      }

      names.add(cells[0].trim());
      coords.add(new double[] {
        Double.parseDouble(cells[1].trim()),
        Double.parseDouble(cells[2].trim()),
        Double.parseDouble(cells[3].trim())
      });
    }
    if (names.isEmpty()) {
      throw new IllegalArgumentException("Inline sensor list has no sensor points.");
    }
  }

  private static String defaultHeader(String phaseColumn, String[] exprs, String[] units) {
    StringBuilder sb = new StringBuilder("sensor,").append(phaseColumn);
    for (int i = 0; i < exprs.length; i++) {
      String label = exprs[i].replaceAll("[^A-Za-z0-9]+", "_").replaceAll("^_+|_+$", "");
      if (label.length() == 0) label = "expr" + (i + 1);
      String unit = i < units.length ? units[i] : "";
      if (unit.length() > 0) label += "_" + unit.replaceAll("[^A-Za-z0-9]+", "_");
      sb.append(",").append(label);
    }
    return sb.toString();
  }

  private static String formatPhase(double value) {
    double rounded = Math.rint(value);
    if (Math.abs(value - rounded) < 1e-9) {
      return String.format(Locale.US, "%.0f", rounded);
    }
    return String.format(Locale.US, "%.12g", value);
  }

  public static void main(String[] args) throws Exception {
    if (args.length < 10) {
      throw new IllegalArgumentException(
          "Usage: ComsolConfiguredSensorEval <input.mph> <dataset> <exprs> <units> " +
          "<solution_indices> <phase_start> <phase_step> <phase_column> <csv_header> <sensors_inline>");
    }

    String input = args[0];
    String modelName = "ConfiguredSensorEval";
    String dataset = args[1].trim();
    String[] exprs = splitList(args[2]);
    String[] units = splitList(args[3]);
    int[] solutionIndices = parseIntList(args[4]);
    double phaseStart = Double.parseDouble(args[5].trim());
    double phaseStep = Double.parseDouble(args[6].trim());
    String phaseColumn = args[7].trim();
    String csvHeader = args[8].trim();
    if (csvHeader.length() == 0) csvHeader = defaultHeader(phaseColumn, exprs, units);
    List<String> sensorNames = new ArrayList<String>();
    List<double[]> sensorCoords = new ArrayList<double[]>();
    readSensorsInline(args[9], sensorNames, sensorCoords);

    if (exprs.length == 0) {
      throw new IllegalArgumentException("Config must contain at least one expression.");
    }

    Model model = null;
    try {
      model = ModelUtil.load(modelName, input);
      System.out.println("CONFIG_SENSOR_EVAL_BEGIN");
      System.out.println("input=" + input);
      System.out.println("dataset=" + dataset);
      System.out.println("sensor_count=" + sensorNames.size());
      System.out.println("exprs=" + Arrays.toString(exprs));
      System.out.println("units=" + Arrays.toString(units));
      System.out.println("solution_indices=" + Arrays.toString(solutionIndices));
      System.out.println("csv_header=" + csvHeader);
      System.out.println("CONFIG_SENSOR_EVAL_CSV_BEGIN");
      System.out.println(csvHeader);

      for (int i = 0; i < sensorNames.size(); i++) {
        String sensorName = sensorNames.get(i);
        double[] coord = sensorCoords.get(i);
        String tag = "config_sensor_eval_" + (i + 1);
        try { model.result().numerical().remove(tag); } catch (Exception ignore) {}
        model.result().numerical().create(tag, "Interp");
        model.result().numerical(tag).set("data", dataset);
        model.result().numerical(tag).set("expr", exprs);
        if (units.length > 0) model.result().numerical(tag).set("unit", units);
        model.result().numerical(tag).set("coord", new double[][] {
          {coord[0]}, {coord[1]}, {coord[2]}
        });

        for (int solIndex : solutionIndices) {
          double phase = phaseStart + (solIndex - 1) * phaseStep;
          double[][] values = model.result().numerical(tag).getReal(false, solIndex);
          System.out.printf(Locale.US, "%s,%s", sensorName, formatPhase(phase));
          for (int r = 0; r < values.length; r++) {
            for (int c = 0; c < values[r].length; c++) {
              System.out.printf(Locale.US, ",%.12g", values[r][c]);
            }
          }
          System.out.println();
        }
      }

      System.out.println("CONFIG_SENSOR_EVAL_CSV_END");
      System.out.println("config_sensor_eval_status=success");
      System.out.println("CONFIG_SENSOR_EVAL_END");
    } catch (Exception ex) {
      System.out.println("config_sensor_eval_status=failed");
      System.out.println("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace();
      throw ex;
    } finally {
      try { if (model != null) ModelUtil.remove(modelName); } catch (Exception ignore) {}
    }
  }
}
