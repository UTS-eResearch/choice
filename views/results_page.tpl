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
  <pre class="results">{{ inputs['msg'] }}</pre>
%end

<!-- Inputs -->

%if 'tmts' in inputs: 
    %if 'gens' in inputs:
<p>You entered the following for choice sets to be constructed.</p>
<div class="container">
    <div class="left">
        <h2>Treatment Combinations Entered</h2> 
        <pre class="results">{{ inputs['tmts'] }}</pre>
    </div>
    <div class="left"> 
        <h2>Sets of Generators Entered</h2>
        <pre class="results">{{ inputs['gens'] }}</pre>
    </div>
<div class="clear_both"></div>
</div>
    %end
%end

%if 'chsets' in inputs:
  <h2>You entered the following choice sets to be checked:</h2>
  <pre class="results">{{ inputs['chsets'] }}</pre>
%end

%if 'det' in inputs:
  <h2>Determinant of C Entered</h2> {{ inputs['det'] }}
%else:
  <p>No determinant entered</p>
%end

<!-- Outputs -->

<h2>Messages from Processing Stage</h2>
<pre class="results">Time taken was {{ time }} seconds. 
{{ outputs['msg'] }}</pre>

%if 'chsets' in outputs:
<h2>Choice Sets Created</h2>
<pre class="results">{{ outputs['chsets'] }}</pre>
%end

<h2>B Matrix</h2>
<pre class="results">{{ outputs['bmat'] }}</pre>

<h2>Lambda Matrix</h2>
<pre class="results">{{ outputs['lmat'] }}</pre>

<h2>C Matrix</h2>
<pre class="results">{{ outputs['cmat'] }}</pre>

<h2>C Inverse</h2>
<pre class="results">{{ outputs['cinv'] }}</pre>

<h2>Correlation Matrix</h2>
<pre class="results">{{ outputs['correln'] }}</pre>

<br>

%include tail

