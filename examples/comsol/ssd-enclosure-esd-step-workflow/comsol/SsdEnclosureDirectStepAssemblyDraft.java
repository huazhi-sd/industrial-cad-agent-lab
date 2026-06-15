import com.comsol.model.*;
import com.comsol.model.util.*;
import java.util.Arrays;

public class SsdEnclosureDirectStepAssemblyDraft {
  public static void main(String[] args) throws Exception {
    try {
      run(args);
    } catch (Throwable ex) {
      System.out.println("SSD_DIRECT_STEP_STATUS=failed");
      System.out.println("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace(System.out);
      throw ex;
    }
  }

  static void block(Model model, String tag, double sx, double sy, double sz, double x, double y, double z) {
    model.component("comp1").geom("geom1").create(tag, "Block");
    model.component("comp1").geom("geom1").feature(tag).set("size", new String[] {
      Double.toString(sx), Double.toString(sy), Double.toString(sz)
    });
    model.component("comp1").geom("geom1").feature(tag).set("base", "center");
    model.component("comp1").geom("geom1").feature(tag).set("pos", new String[] {
      Double.toString(x), Double.toString(y), Double.toString(z)
    });
    model.component("comp1").geom("geom1").feature(tag).set("selresult", true);
    model.component("comp1").geom("geom1").feature(tag).set("selresultshow", "all");
  }

  public static void run(String[] args) throws Exception {
    String stepPath = args != null && args.length > 0
      ? args[0]
      : "D:\\cdxwork\\comsol-step-import-test\\transparent_pc_m2_2280_ssd_enclosure_assembly.step";

    Model model = ModelUtil.create("SsdEnclosureDirectStepAssemblyDraft");
    model.label("ssd_enclosure_direct_step_assembly_draft.mph");

    model.component().create("comp1", true);
    model.component("comp1").geom().create("geom1", 3);
    model.component("comp1").geom("geom1").lengthUnit("mm");

    model.component("comp1").geom("geom1").create("imp1", "Import");
    model.component("comp1").geom("geom1").feature("imp1").set("filename", stepPath);
    model.component("comp1").geom("geom1").feature("imp1").set("selresult", true);
    model.component("comp1").geom("geom1").feature("imp1").set("selresultshow", "all");
    model.component("comp1").geom("geom1").feature("imp1").importData();

    // Match the human workflow: import product first, then create the air domain in COMSOL.
    block(model, "air_after_import", 135.0, 64.0, 34.0, 0.0, 0.0, 9.0);

    // Keep the imported product as an assembly instead of forcing a union that slices it heavily.
    model.component("comp1").geom("geom1").feature("fin").set("action", "assembly");
    model.component("comp1").geom("geom1").feature("fin").set("imprint", false);
    model.component("comp1").geom("geom1").run();

    System.out.println("SSD_DIRECT_STEP_STATUS=geometry_success");
    System.out.println("step_path=" + stepPath);
    System.out.println("geom_is_assembly=" + model.component("comp1").geom("geom1").isAssembly());
    System.out.println("geom_has_cad_rep=" + model.component("comp1").geom("geom1").hasCadRep());
    System.out.println("geom_features=" + Arrays.toString(model.component("comp1").geom("geom1").feature().tags()));
    System.out.println("geom_object_names=" + Arrays.toString(model.component("comp1").geom("geom1").objectNames()));
    System.out.println("geom_domains=" + model.component("comp1").geom("geom1").getNDomains());
    System.out.println("geom_boundaries=" + model.component("comp1").geom("geom1").getNBoundaries());
    System.out.println("geom_bbox=" + Arrays.toString(model.component("comp1").geom("geom1").getBoundingBox()));

    model.component("comp1").physics().create("es", "Electrostatics", "geom1");

    try {
      String mphPath = "D:\\cdxwork\\comsol-step-import-test\\ssd_enclosure_direct_step_assembly_draft.mph";
      model.save(mphPath);
      System.out.println("saved_mph=" + mphPath);
    } catch (Throwable saveEx) {
      System.out.println("WARN_SAVE_MPH_FAILED=" + saveEx.getClass().getName() + ": " + saveEx.getMessage());
    }

    ModelUtil.remove("SsdEnclosureDirectStepAssemblyDraft");
  }
}
