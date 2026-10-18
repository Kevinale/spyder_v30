import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.program.model.scalar.Scalar;
import ghidra.app.decompiler.*;
import java.io.*;import java.util.*;
public class UsbFollowup extends GhidraScript {
 public void run() throws Exception {
 PrintWriter w=new PrintWriter(new FileWriter(getScriptArgs()[0]));Set<Function> selected=new LinkedHashSet<>();
 for(String a:new String[]{"1400350c4","1400031dc","140034f44"})for(Reference r:getReferencesTo(toAddr(a))){Function f=getFunctionContaining(r.getFromAddress());w.println("TRANSLATOR_XREF "+a+" "+r+" "+(f==null?"":f.getName()));if(f!=null)selected.add(f);}
 InstructionIterator ii=currentProgram.getListing().getInstructions(true);while(ii.hasNext()){Instruction i=ii.next();for(int o=0;o<i.getNumOperands();o++)for(Object v:i.getOpObjects(o))if(v instanceof Scalar){long n=((Scalar)v).getUnsignedValue();if(n==0x204||n==0x205){Function f=getFunctionContaining(i.getAddress());w.println("SCALAR "+i.getAddress()+" "+i+" "+(f==null?"":f.getName()));if(f!=null)selected.add(f);}}}
 for(String ea:new String[]{"140022350","140025750","14002449c","140024100","140004680","140023138","1400215b0"}){Function extra=getFunctionAt(toAddr(ea));if(extra!=null)selected.add(extra);}
 DecompInterface dc=new DecompInterface();dc.openProgram(currentProgram);for(Function f:selected){w.println("DECOMPILE "+f.getEntryPoint()+" "+f.getName());DecompileResults r=dc.decompileFunction(f,30,monitor);if(r.decompileCompleted())w.println(r.getDecompiledFunction().getC());}dc.dispose();w.close();
 }
}
