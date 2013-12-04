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

%if 'msg' in inputs:
<h2>Messages from Input Stage</h2>
<div class="results">
{{ inputs['msg'] }}
</div>
%end

<h2>Messages from Processing Stage</h2>
<div class="results">Time taken was {{ time }} seconds. 
{{ outputs['msg'] }}
</div>

%if 'tmts' in inputs:
    %if 'gens' in inputs:
    <h2>Choice Sets Entered</h2>
    <div class="results">
    <table border=1>
    <tr><th>Treatment Combinations</th><th>Sets of Generators</th></tr>
    <tr><td>{{ inputs['tmts'] }}</td><td>{{ inputs['gens'] }}</td></tr>
    </table>    
    </div>
    %end
%end

%if 'chsets' in inputs:
  <h2>Choice Sets Entered</h2>
  <div class="results">{{ inputs['chsets'] }}</div>
%else:
  <h2>Choice Sets Created</h2>
  <div class="results">{{ outputs['chsets'] }}</div>
%end

%if 'det' in inputs:
  <h2>Determinant of C Entered</h2> {{ inputs['det'] }}
%end

<h2>Correlation Matrix</h2>
<div class="results">{{ outputs['correln'] }}</div>

<h2>C Inverse</h2>
<div class="results">{{ outputs['cinv'] }}</div>

<h2>C Matrix</h2>
<div class="results">{{ outputs['cmat'] }}</div>

<h2>B Matrix</h2>
<div class="results">{{ outputs['bmat'] }}</div>

<h2>Lambda Matrix</h2>
<div class="results">{{ outputs['lmat'] }}</div>

<br>

%include tail

