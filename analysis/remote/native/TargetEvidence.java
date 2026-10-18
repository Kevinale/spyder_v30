import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.*;
import java.io.*;
import java.util.*;
public class TargetEvidence extends GhidraScript {
 public void run() throws Exception {
 PrintWriter w=new PrintWriter(new FileWriter(getScriptArgs()[0]));
 DecompInterface dc=new DecompInterface();dc.openProgram(currentProgram);
 Set<Function> fs=new LinkedHashSet<>();
 for(int i=1;i<getScriptArgs().length;i++){Address a=toAddr(getScriptArgs()[i]);Function f=getFunctionContaining(a);if(f!=null)fs.add(f);for(Reference r:getReferencesTo(a)){w.println("XREF "+a+" "+r.getFromAddress());f=getFunctionContaining(r.getFromAddress());if(f!=null)fs.add(f);}}
 for(Function f:fs){w.println("FUNCTION "+f.getEntryPoint()+" "+f.getName());DecompileResults d=dc.decompileFunction(f,60,monitor);if(d.decompileCompleted())w.println(d.getDecompiledFunction().getC());}
 dc.dispose();w.close();
 }
}
