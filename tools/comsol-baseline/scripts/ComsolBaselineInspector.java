import com.comsol.model.*;
import com.comsol.model.util.*;
import java.io.*;
import java.lang.reflect.*;
import java.util.*;

public class ComsolBaselineInspector {
  private static PrintWriter out;

  private static void line(String s) {
    System.out.println(s);
    if (out != null) out.println(s);
  }

  private static void section(String title) {
    line("");
    line("## " + title);
  }

  private static Object call(Object obj, String method) {
    if (obj == null) return null;
    try {
      Method m = obj.getClass().getMethod(method);
      return m.invoke(obj);
    } catch (Exception ex) {
      return null;
    }
  }

  private static Object callString(Object obj, String method, String arg) {
    if (obj == null) return null;
    try {
      Method m = obj.getClass().getMethod(method, String.class);
      return m.invoke(obj, arg);
    } catch (Exception ex) {
      return null;
    }
  }

  private static String str(Object obj, String method) {
    Object v = call(obj, method);
    return v == null ? "" : String.valueOf(v);
  }

  private static String strArg(Object obj, String method, String arg) {
    Object v = callString(obj, method, arg);
    return v == null ? "" : String.valueOf(v);
  }

  private static String[] tags(Object list) {
    Object v = call(list, "tags");
    if (v instanceof String[]) return (String[]) v;
    return new String[0];
  }

  private static int size(Object list) {
    Object v = call(list, "size");
    if (v instanceof Integer) return ((Integer)v).intValue();
    return tags(list).length;
  }

  private static Object byTag(Object list, String tag) {
    Object v = callString(list, "get", tag);
    if (v != null) return v;
    return null;
  }

  private static String selectionEntities(Object entity) {
    try {
      Object sel = call(entity, "selection");
      Object ents = call(sel, "entities");
      if (ents instanceof int[]) return Arrays.toString((int[]) ents);
      return ents == null ? "" : String.valueOf(ents);
    } catch (Exception ex) {
      return "";
    }
  }

  private static void listGeneric(String title, Object list, String indent) {
    String[] t = tags(list);
    line(indent + title + "_count=" + (t.length > 0 ? t.length : size(list)));
    if (t.length == 0) {
      line(indent + title + "_tags=<none-or-unavailable>");
      return;
    }
    for (int i = 0; i < t.length; i++) {
      Object obj = byTag(list, t[i]);
      String name = str(obj, "name");
      String op = str(obj, "operation");
      line(String.format(Locale.US, "%s- %s[%d] tag=%s%s%s",
          indent, title, i, t[i],
          op.length() > 0 ? " op=" + op : "",
          name.length() > 0 ? " name=" + name : ""));
      String sel = selectionEntities(obj);
      if (sel.length() > 0) line(indent + "  selection=" + sel);
    }
  }

  private static void listParameters(Model model) {
    section("Global Parameters");
    try {
      String[] vars = model.param().varnames();
      line("parameter_count=" + vars.length);
      for (String v : vars) {
        String val = "";
        String desc = "";
        try { val = model.param().get(v); } catch (Exception ex) {}
        try { desc = model.param().descr(v); } catch (Exception ex) {}
        line("- " + v + " = " + val + (desc.length() > 0 ? " // " + desc : ""));
      }
    } catch (Exception ex) {
      line("WARN parameter listing failed: " + ex.getMessage());
    }
  }

  private static void listComponent(Model model, String compTag) {
    section("Component " + compTag);
    Object comp = byTag(model.component(), compTag);
    if (comp == null) {
      line("WARN component unavailable by tag: " + compTag);
      return;
    }
    line("component_tag=" + str(comp, "tag"));
    line("component_name=" + str(comp, "name"));

    section("Geometry in " + compTag);
    Object geomList = call(comp, "geom");
    listGeneric("geometry", geomList, "");
    for (String geomTag : tags(geomList)) {
      Object geom = byTag(geomList, geomTag);
      Object featureList = call(geom, "feature");
      if (featureList != null) {
        line("geometry " + geomTag + " features:");
        listGeneric("feature", featureList, "  ");
      }
    }

    section("Materials in " + compTag);
    listGeneric("material", call(comp, "material"), "");

    section("Physics in " + compTag);
    Object physicsList = call(comp, "physics");
    listGeneric("physics", physicsList, "");
    for (String physTag : tags(physicsList)) {
      Object phys = byTag(physicsList, physTag);
      Object featureList = call(phys, "feature");
      if (featureList != null) {
        line("physics " + physTag + " features:");
        String[] ftags = tags(featureList);
        line("  feature_count=" + ftags.length);
        for (int i = 0; i < ftags.length; i++) {
          Object feat = byTag(featureList, ftags[i]);
          String name = str(feat, "name");
          String op = str(feat, "operation");
          line(String.format(Locale.US, "  - feature[%d] tag=%s%s%s", i, ftags[i],
              op.length() > 0 ? " op=" + op : "",
              name.length() > 0 ? " name=" + name : ""));
          String sel = selectionEntities(feat);
          if (sel.length() > 0) line("    selection=" + sel);
          String icoil = strArg(feat, "getString", "ICoil");
          if (icoil.length() > 0) line("    ICoil=" + icoil);
          Object childList = call(feat, "feature");
          String[] childTags = tags(childList);
          if (childTags.length > 0) {
            line("    child_tags=" + Arrays.toString(childTags));
          }
        }
      }
    }

    section("Meshes in " + compTag);
    Object meshList = call(comp, "mesh");
    listGeneric("mesh", meshList, "");
    for (String meshTag : tags(meshList)) {
      Object mesh = byTag(meshList, meshTag);
      Object featureList = call(mesh, "feature");
      if (featureList != null) {
        line("mesh " + meshTag + " features:");
        listGeneric("feature", featureList, "  ");
      }
    }
  }

  private static void listStudies(Model model) {
    section("Studies");
    Object studyList = model.study();
    listGeneric("study", studyList, "");
    for (String studyTag : tags(studyList)) {
      Object study = byTag(studyList, studyTag);
      Object featureList = call(study, "feature");
      if (featureList != null) {
        line("study " + studyTag + " features:");
        listGeneric("feature", featureList, "  ");
      }
    }
  }

  private static void listResults(Model model) {
    section("Results");
    Object result = model.result();
    listGeneric("dataset", call(result, "dataset"), "");
    Object numerical = call(result, "numerical");
    listGeneric("numerical", numerical, "");
    for (String tag : tags(numerical)) {
      Object n = byTag(numerical, tag);
      String expr = strArg(n, "getString", "expr");
      String data = strArg(n, "getString", "data");
      if (expr.length() > 0) line("  numerical " + tag + " expr=" + expr);
      if (data.length() > 0) line("  numerical " + tag + " data=" + data);
    }
    listGeneric("export", call(result, "export"), "");
  }

  public static void main(String[] args) throws Exception {
    if (args.length < 1) {
      throw new IllegalArgumentException("Usage: ComsolBaselineInspector <input.mph> [report.txt]");
    }
    String input = args[0];
    String report = args.length >= 2 ? args[1] : "<stdout-only>";
    if (args.length >= 2 && !"-".equals(args[1])) {
      try {
        out = new PrintWriter(new OutputStreamWriter(new FileOutputStream(report), "UTF-8"));
      } catch (Exception ex) {
        out = null;
        System.out.println("WARN report_file_write_disabled=" + ex.getClass().getName() + ": " + ex.getMessage());
        report = "<stdout-only>";
      }
    }

    line("# COMSOL Baseline Inspector");
    line("input=" + input);
    line("report=" + report);

    Model model = null;
    try {
      model = ModelUtil.load("BaselineModel", input);
      line("load_status=success");
      line("model_tag=" + model.tag());
      line("model_name=" + model.name());
      try { line("model_label=" + model.label()); } catch (Exception ex) {}

      listParameters(model);
      section("Components");
      Object comps = model.component();
      listGeneric("component", comps, "");
      for (String compTag : tags(comps)) {
        listComponent(model, compTag);
      }
      listStudies(model);
      listResults(model);

      line("");
      line("baseline_status=success");
    } catch (Exception ex) {
      line("baseline_status=failed");
      line("ERROR " + ex.getClass().getName() + ": " + ex.getMessage());
      ex.printStackTrace();
      throw ex;
    } finally {
      try { if (model != null) ModelUtil.remove("BaselineModel"); } catch (Exception ignore) {}
      if (out != null) {
        out.flush();
        out.close();
      }
    }
  }
}
