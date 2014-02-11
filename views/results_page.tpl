%include head
%include top.tpl title='Discrete Choice Experiment Results'

<p><a href="../">Return to Discrete Choice Experiments</a>
&nbsp; 
%if test:
<span style="color:red;font-weight:bold;">Running in TEST mode! 
{{ outputs['errors'] }} 
</span>
%end 
</p>

<h2>Messages from Input Stage</h2>
%if 'msg' in inputs:
  <div class="results">{{ inputs['msg'] }}</div>
%end

<!-- Inputs -->

%if 'tmts' in inputs: 
    %if 'gens' in inputs:
<p>You entered the following for choice sets to be constructed.</p>
<div class="container">
    <div class="left">
        <h2>Treatment Combinations Entered</h2> 
        <div class="results">{{ inputs['tmts'] }}</div>
    </div>
    <div class="left"> 
        <h2>Sets of Generators Entered</h2>
        <div class="results">{{ inputs['gens'] }}</div>
    </div>
<div class="clear_both"></div>
</div>
    %end
%end

%if 'chsets' in inputs:
  <h2>You entered the following choice sets to be checked:</h2>
  <div class="results">{{ inputs['chsets'] }}</div>
%end

%if 'det' in inputs:
  <h2>Determinant of C Entered</h2> {{ inputs['det'] }}
%else:
  <p>None entered</p>
%end

<!-- Outputs -->

<h2>Messages from Processing Stage</h2>
<div class="results">Time taken was {{ time }} seconds. 
{{ outputs['msg'] }}</div>

%if 'chsets' in outputs:
<h2>Choice Sets Created</h2>
<div class="results">{{ outputs['chsets'] }}</div>
%end

<h2>B Matrix</h2>
<div class="results">{{ outputs['bmat'] }}</div>

<h2>Lambda Matrix</h2>
<div class="results">{{ outputs['lmat'] }}</div>

<h2>C Matrix</h2>
<div class="results">{{ outputs['cmat'] }}</div>

<h2>C Inverse</h2>
<div class="results">{{ outputs['cinv'] }}</div>

<h2>Correlation Matrix</h2>
<div class="results">{{ outputs['correln'] }}</div>





<br>

%include tail

