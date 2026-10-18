import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.address.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.*;
import java.io.*;
import java.util.*;
public class RangeEvidence extends GhidraScript {
 public void run() throws Exception {
 PrintWriter w=new PrintWriter(new FileWriter(getScriptArgs()[0]));
 DecompInterface dc=new DecompInterface();dc.openProgram(currentProgram);
 Set<Function> fs=new LinkedHashSet<>();
 FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);while(fi.hasNext()){Function f=fi.next();long a=f.getEntryPoint().getOffset();if(a>=Long.parseLong(getScriptArgs()[1],16)&&a<Long.parseLong(getScriptArgs()[2],16))fs.add(f);}
 for(Function f:fs){w.println("FUNCTION "+f.getEntryPoint()+" "+f.getName());DecompileResults d=dc.decompileFunction(f,60,monitor);if(d.decompileCompleted())w.println(d.getDecompiledFunction().getC());}
 dc.dispose();w.close();
 }
}
