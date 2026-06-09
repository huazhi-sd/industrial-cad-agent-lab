import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.*;

public class ComsolConfiguredSingleSolve {
  private static String[] splitList(String raw) {
    if (raw == null || raw.trim().isEmpty()) return new String[0];
    String[] items = raw.split(",");
    for (int i = 0; i < items.length; i++) items[i] = items[i].trim();
    return items;
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

  private static String join(String[] xs) {
    return xs == null ? "<null>" : Arrays.toString(xs);
  }

  public static void main(String[] args) throws Exception {
    if (args.length < 13) {
      throw new IllegalArgumentException(
          "Usage: ComsolConfiguredSingleSolve <input.mph> <study_tag> <param_feature_tag> " +
          "<param_name> <param_value> <param_unit> <result_dataset> <exprs> <units> " +
          "<phase_column> <csv_header> <sensors_inline> <model_name>");
    }

    String input = args[0];
    String studyTag = args[1].trim();
    String paramFeatureTag = args[2].trim();
    String paramName = args[3].trim();
    String paramValue = args[4].trim();
    String paramUnit = args[5].trim();
    if (paramUnit.equals("__EMPTY__")) paramUnit = "";
    String resultDataset = args[6].trim();
    String[] exprs = splitList(args[7]);
    String[] units = splitList(args[8]);
    String phaseColumn = args[9].trim();
    String csvHeader = args[10].trim();
    String sensorsInline = args[11];
    String modelName = args[12].trim();
    if (modelName.length() == 0) modelName = "ConfiguredSingleSolve";

    List<String> sensorNames = new ArrayList<String>();
    List<double[]> sensorCoords = new ArrayList<double[]>();
    readSensorsInline(sensorsInline, sensorNames, sensorCoords);

    Model model = null;
    try {
      model = ModelUtil.loadCopy(modelName, input);
      System.out.println("CONFIG_SINGLE_SOLVE_BEGIN");
      System.out.println("input=" + input);
      System.out.println("study_tag=" + studyTag);
      System.out.println("param_feature_tag=" + paramFeatureTag);
      System.out.println("param_name=" + paramName);
      System.out.println("param_value=" + paramValue);
      System.out.println("param_unit=" + paramUnit);
      System.out.println("result_dataset=" + resultDataset);
      System.out.println("exprs=" + Arrays.toString(exprs));
      System.out.println("units=" + Arrays.toString(units));
      System.out.println("sensor_count=" + sensorNames.size());

      try {
        StudyFeature param = model.study(studyTag).feature(paramFeatureTag);
        System.out.println("param_before_pname=" + join(param.getStringArray("pname")));
        System.out.println("param_before_plistarr=" + join(param.getStringArray("plistarr")));
        param.set("pname", new String[] {paramName});
        param.set("plistarr", new String[] {paramValue});
        param.set("punit", new String[] {paramUnit});
        System.out.println("param_after_pname=" + join(param.getStringArray("pname")));
        System.out.println("param_after_plistarr=" + join(param.getStringArray("plistarr")));
      } catch (Exception ex) {
        System.out.println("config_param_setup_status=failed");
        System.out.println("config_param_setup_error=" + ex.getClass().getName() + ": " + ex.getMessage());
        throw ex;
      }

      System.out.println("study_run_begin=" + studyTag);
      model.study(studyTag).run();
      System.out.println("study_run_status=success");

      System.out.println("CONFIG_SINGLE_SOLVE_CSV_BEGIN");
      System.out.println(csvHeader);
      for (int i = 0; i < sensorNames.size(); i++) {
        String sensorName = sensorNames.get(i);
        double[] coord = sensorCoords.get(i);
        String tag = "config_single_solve_" + (i + 1);
        try { model.result().numerical().remove(tag); } catch (Exception ignore) {}
        model.result().numerical().create(tag, "Interp");
        model.result().numerical(tag).set("data", resultDataset);
        model.result().numerical(tag).set("expr", exprs);
        if (units.length > 0) model.result().numerical(tag).set("unit", units);
        model.result().numerical(tag).set("coord", new double[][] {
          {coord[0]}, {coord[1]}, {coord[2]}
        });

        double[][] values = model.result().numerical(tag).getReal();
        System.out.printf(Locale.US, "%s,%s", sensorName, paramValue);
        for (int r = 0; r < values.length; r++) {
          for (int c = 0; c < values[r].length; c++) {
            System.out.printf(Locale.US, ",%.12g", values[r][c]);
          }
        }
        System.out.println();
      }
      System.out.println("CONFIG_SINGLE_SOLVE_CSV_END");
      System.out.println("config_single_solve_status=success");
      System.out.println("CONFIG_SINGLE_SOLVE_END");
    } catch (Exception ex) {
      System.out.println("config_single_solve_status=failed");
      System.out.println("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace();
      throw ex;
    } finally {
      try { if (model != null) ModelUtil.remove(modelName); } catch (Exception ignore) {}
    }
  }
}
