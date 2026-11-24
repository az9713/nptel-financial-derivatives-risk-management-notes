/* Educational one-period models; no network access or market-data dependency. */
(() => {
  const value = id => Number(document.getElementById(id)?.value);
  const write = (id, text) => {const node = document.getElementById(id); if (node) node.textContent = text;};
  function carry() {
    if (!document.getElementById('carry-spot')) return;
    const spot=value('carry-spot'), rate=value('carry-rate')/100, time=value('carry-time');
    const valid=[spot,rate,time].every(Number.isFinite)&&spot>0&&time>=0;
    const forward=valid ? spot*Math.exp(rate*time) : NaN;
    write('carry-forward', !valid ? 'Enter finite values, positive spot, and nonnegative time.' :
      !Number.isFinite(forward)||forward<=0 ? 'The computed price exceeds numerical range. Use smaller magnitudes.' : forward.toFixed(6));
  }
  function tree() {
    if (!document.getElementById('tree-spot')) return;
    const spot=value('tree-spot'), up=value('tree-up'), down=value('tree-down');
    const strike=value('tree-strike'), growth=value('tree-growth');
    if (![spot,up,down,strike,growth].every(Number.isFinite)||spot<=0||down<=0||strike<0||!(down<growth&&growth<up)) {
      write('tree-error','The model requires positive spot and down factor, nonnegative strike, and down < bank growth < up.');
      ['tree-price','tree-delta','tree-probability'].forEach(id=>write(id,'—'));
      return;
    }
    const cu=Math.max(spot*up-strike,0), cd=Math.max(spot*down-strike,0);
    const delta=(cu-cd)/(spot*(up-down));
    const bank=(up*cd-down*cu)/((up-down)*growth);
    const probability=(growth-down)/(up-down);
    const price=delta*spot+bank;
    const error=Math.max(Math.abs(delta*spot*up+bank*growth-cu),Math.abs(delta*spot*down+bank*growth-cd));
    if (![cu,cd,delta,bank,probability,price,error].every(Number.isFinite)) {
      write('tree-error','The computed hedge exceeds numerical range. Use smaller magnitudes.');
      ['tree-price','tree-delta','tree-probability'].forEach(id=>write(id,'—'));
      return;
    }
    write('tree-price',price.toFixed(6));write('tree-delta',delta.toFixed(6));
    write('tree-probability',probability.toFixed(6));
    write('tree-error',`Replication residual: ${error.toExponential(2)}. The weight is a pricing probability; holdings replicate both states.`);
  }
  document.querySelectorAll('.lab-grid input').forEach(input=>input.addEventListener('input',()=>{carry();tree();}));
  carry();tree();
})();
