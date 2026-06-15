import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.Arrays;

public class ComsolStepImportInspector {
  public static void main(String[] args) throws Exception {
    try {
      run(args);
    } catch (Throwable ex) {
      System.out.println("STEP_IMPORT_STATUS=failed");
      System.out.println("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace(System.out);
      throw ex;
    }
  }

  public static void run(String[] args) throws Exception {
    String stepPath = args != null && args.length > 0
      ? args[0]
      : "D:\\cdxwork\\comsol-step-import-test\\ssd_enclosure_esd_sim_simplified.step";

    Model model = ModelUtil.create("ComsolStepImportInspector");
    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").lengthUnit("mm");

    model.component("comp1").geom("geom1").create("imp1", "Import");
    model.component("comp1").geom("geom1").feature("imp1").set("filename", stepPath);
    model.component("comp1").geom("geom1").feature("imp1").set("selresult", true);
    model.component("comp1").geom("geom1").feature("imp1").set("selresultshow", "all");
    model.component("comp1").geom("geom1").feature("imp1").importData();
    try {
      model.component("comp1").geom("geom1").feature("fin").set("action", "assembly");
      model.component("comp1").geom("geom1").feature("fin").set("imprint", false);
      System.out.println("finalization_action=assembly");
    } catch (Throwable finEx) {
      System.out.println("finalization_action_error=" + finEx.getClass().getName() + ": " + finEx.getMessage());
    }
    model.component("comp1").geom("geom1").run();

    System.out.println("STEP_IMPORT_STATUS=success");
    System.out.println("step_path=" + stepPath);
    System.out.println("geom_features=" + Arrays.toString(model.component("comp1").geom("geom1").feature().tags()));
    probeImportSelection(model, "input");
    probeImportSelection(model, "output");
    probeImportSelection(model, "dom");
    probeImportSelection(model, "bnd");
    probeImportSelection(model, "selection");
    System.out.println("import_feature_objects=" + Arrays.toString(model.component("comp1").geom("geom1").feature("imp1").objectNames()));
    System.out.println("geom_object_names=" + Arrays.toString(model.component("comp1").geom("geom1").objectNames()));
    System.out.println("geom_is_assembly=" + model.component("comp1").geom("geom1").isAssembly());
    System.out.println("geom_has_cad_rep=" + model.component("comp1").geom("geom1").hasCadRep());
    System.out.println("geom_domains=" + model.component("comp1").geom("geom1").getNDomains());
    System.out.println("geom_boundaries=" + model.component("comp1").geom("geom1").getNBoundaries());
    System.out.println("geom_edges=" + model.component("comp1").geom("geom1").getNEdges());
    System.out.println("geom_vertices=" + model.component("comp1").geom("geom1").getNVertices());
    System.out.println("geom_bbox=" + Arrays.toString(model.component("comp1").geom("geom1").getBoundingBox()));
    String[] objects = model.component("comp1").geom("geom1").objectNames();
    for (String objName : objects) {
      GeomObject obj = model.component("comp1").geom("geom1").object(objName);
      System.out.println(
        "object_info name=" + objName
        + " bbox=" + Arrays.toString(obj.getBoundingBox())
        + " domains=" + obj.getNDomains()
        + " boundaries=" + obj.getNBoundaries()
        + " edges=" + obj.getNEdges()
        + " vertices=" + obj.getNVertices()
      );
    }

    testBoxSelection(model, "box_air", new double[] {-67.51, 67.51, -32.01, 32.01, -8.01, 26.01});
    testBoxSelection(model, "box_bottom_shell", new double[] {-56.36, 56.01, -19.01, 19.01, -0.01, 10.21});
    testBoxSelection(model, "box_top_shell", new double[] {-56.01, 56.01, -19.01, 19.01, 5.91, 12.01});
    testBoxSelection(model, "box_usb_c_shell", new double[] {-56.01, -48.49, -4.41, 4.41, 3.99, 7.21});
    testBoxSelection(model, "box_tail_screw", new double[] {42.84, 47.16, -2.16, 2.16, 4.04, 7.04});
    System.out.println("component_selection_tags=" + Arrays.toString(model.component("comp1").selection().tags()));
    System.out.println("global_selection_tags=" + Arrays.toString(model.selection().tags()));
    System.out.println("imp_domain_entities=" + Arrays.toString(model.selection("geom1_imp1_dom").entities(3)));
    System.out.println("imp_boundary_entities=" + Arrays.toString(model.selection("geom1_imp1_bnd").entities(2)));

    ModelUtil.remove("ComsolStepImportInspector");
  }

  private static void testBoxSelection(Model model, String tag, double[] bbox) {
    try {
      model.component("comp1").selection().create(tag, "Box");
      model.component("comp1").selection(tag).set("entitydim", "3");
      model.component("comp1").selection(tag).set("condition", "inside");
      model.component("comp1").selection(tag).set("xmin", Double.toString(bbox[0]));
      model.component("comp1").selection(tag).set("xmax", Double.toString(bbox[1]));
      model.component("comp1").selection(tag).set("ymin", Double.toString(bbox[2]));
      model.component("comp1").selection(tag).set("ymax", Double.toString(bbox[3]));
      model.component("comp1").selection(tag).set("zmin", Double.toString(bbox[4]));
      model.component("comp1").selection(tag).set("zmax", Double.toString(bbox[5]));
      System.out.println("box_selection tag=" + tag + " domains=" + Arrays.toString(model.component("comp1").selection(tag).entities(3)));
    } catch (Throwable ex) {
      System.out.println("box_selection_error tag=" + tag + " error=" + ex.getClass().getName() + ": " + ex.getMessage());
    }
  }

  private static void probeImportSelection(Model model, String name) {
    try {
      GeomObjectSelection sel = model.component("comp1").geom("geom1").feature("imp1").selection(name);
      System.out.println("import_feature_selection_probe name=" + name + " objects=" + Arrays.toString(sel.objects()));
    } catch (Throwable ex) {
      System.out.println("import_feature_selection_probe_error name=" + name + " error=" + ex.getClass().getName() + ": " + ex.getMessage());
    }
  }
}
