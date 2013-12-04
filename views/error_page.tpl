%include head
%include top.tpl title='Discrete Choice Experiments'

<p>Click here to return to the <a href="/choice">Choice Experiment Page</a>
</p>

<p>Oops, an error seems to have occurred. Please copy the error below and email 
to the authors of this site. 
</p>

<p>Date and time: {{ now }} </p>

<pre>
{{ errors }}
</pre>

<!-- Were included in the pre above.
{ errors['returncode'] }
{ errors['output'] }
-->

%include tail

