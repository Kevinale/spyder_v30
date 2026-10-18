import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import ghidra.app.decompiler.*;
import java.io.*;
import java.util.*;
public class UsbEvidence extends GhidraScript {
 public void run() throws Exception {
  String out=getScriptArgs()[0]; PrintWriter w=new PrintWriter(new FileWriter(out));
  w.println("PROGRAM "+currentProgram.getName()+" IMAGEBASE "+currentProgram.getImageBase());
  FunctionIterator fi=currentProgram.getFunctionManager().getFunctions(true);
  while(fi.hasNext()){Function f=fi.next();w.println("FUNCTION "+f.getEntryPoint()+" "+f.getName());}
  Set<Function> selected=new LinkedHashSet<>();
  FunctionIterator ex=currentProgram.getFunctionManager().getFunctions(true); while(ex.hasNext()){Function f=ex.next();if(f.getName().matches("(?i).*(InterposerBackend|DllGetClassObject).*"))selected.add(f);}
  SymbolIterator si=currentProgram.getSymbolTable().getAllSymbols(true);
  while(si.hasNext()){Symbol s=si.next(); if(s.getName().matches("(?i).*(usb|midi|firmware|preset|parameter|controltransfer|bulk|interrupt|descriptor).*")) {w.println("SYMBOL "+s.getAddress()+" "+s.getName());for(Reference r:s.getReferences()){Function f=currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress());w.println(" SYMBOL_XREF "+r.getFromAddress()+" "+(f==null?"":f.getName()));if(f!=null)selected.add(f);}}}
  DataIterator di=currentProgram.getListing().getDefinedData(true);
  while(di.hasNext()){Data d=di.next();Object v=d.getValue();if(v instanceof String && v.toString().matches("(?is).*(usb|midi|firmware|preset|parameter|knob|spider|sysex|sample rate|latency).*")){w.println("STRING "+d.getAddress()+" "+v.toString().replace("\n","\\n"));for(Reference r:getReferencesTo(d.getAddress())){Function f=currentProgram.getFunctionManager().getFunctionContaining(r.getFromAddress());w.println(" STRING_XREF "+r.getFromAddress()+" "+(f==null?"":f.getName()));if(f!=null)selected.add(f);}}}
  DecompInterface dc=new DecompInterface();dc.openProgram(currentProgram);int n=0;
  for(Function f:selected){if(n++>=100)break;DecompileResults res=dc.decompileFunction(f,30,monitor);w.println("DECOMPILE "+f.getEntryPoint()+" "+f.getName());if(res.decompileCompleted())w.println(res.getDecompiledFunction().getC());else w.println(res.getErrorMessage());}
  dc.dispose();w.close();
 }
}
