import ghidra.app.script.GhidraScript;import ghidra.program.model.listing.*;import ghidra.program.model.scalar.Scalar;import ghidra.app.decompiler.*;import java.io.*;import java.util.*;
public class SystemSettingEvidence extends GhidraScript {
 public void run() throws Exception {
  PrintWriter w=new PrintWriter(getScriptArgs()[0]);Set<Function> fs=new LinkedHashSet<>();
  InstructionIterator ii=currentProgram.getListing().getInstructions(true);
  while(ii.hasNext()){
   Instruction i=ii.next();if(!i.getMnemonicString().equals("CALL"))continue;
   for(int o=0;o<i.getNumOperands();o++)for(Object v:i.getOpObjects(o))if(v instanceof Scalar){long n=((Scalar)v).getUnsignedValue();if(n==0x94||n==0x98){Function f=getFunctionContaining(i.getAddress());w.println("CALL_SLOT "+i.getAddress()+" "+i+" "+(f==null?"":f.getName()));if(f!=null)fs.add(f);}}
  }
  for(String a:new String[]{"10084d20","10097a40"}){Function f=getFunctionAt(toAddr(a));if(f!=null)fs.add(f);}
  DecompInterface dc=new DecompInterface();dc.openProgram(currentProgram);
  for(Function f:fs){w.println("FUNCTION "+f.getEntryPoint()+" "+f.getName());DecompileResults d=dc.decompileFunction(f,30,monitor);if(d.decompileCompleted())w.println(d.getDecompiledFunction().getC());}
  dc.dispose();w.close();
 }
}
