import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.app.decompiler.*;
import java.io.*;import java.util.*;
public class MonitorGainEvidence extends GhidraScript {
 public void run() throws Exception {
 PrintWriter w=new PrintWriter(getScriptArgs()[0]);Set<Function> selected=new LinkedHashSet<>();
 InstructionIterator ii=currentProgram.getListing().getInstructions(true);
 while(ii.hasNext()){Instruction i=ii.next();for(int o=0;o<i.getNumOperands();o++)for(Object v:i.getOpObjects(o))if(v instanceof Scalar){long n=((Scalar)v).getUnsignedValue();if(n==0x280||n==0x281){Function f=getFunctionContaining(i.getAddress());w.println("SCALAR "+i.getAddress()+" "+i+" "+(f==null?"":f.getName()));if(f!=null)selected.add(f);}}}
 for(Function f:selected){w.println("FUNCTION_XREFS "+f.getEntryPoint());for(Reference r:getReferencesTo(f.getEntryPoint()))w.println(r);}
 DecompInterface dc=new DecompInterface();dc.openProgram(currentProgram);for(Function f:selected){w.println("DECOMPILE "+f.getEntryPoint()+" "+f.getName());DecompileResults r=dc.decompileFunction(f,30,monitor);if(r.decompileCompleted())w.println(r.getDecompiledFunction().getC());}dc.dispose();w.close();
 }
}
