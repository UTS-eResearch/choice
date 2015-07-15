%include head
%include top.tpl title='Discrete Choice Experiments'

<p>Click here to return to the <a href="/choice">Choice Experiment Page</a>
</p>

<p>Errors are listed below:
</p>

<pre>
{{ errors }}
</pre>

<p>Date and time: {{ now }} </p>

<!-- Were included in the pre above.
{ errors['returncode'] }
{ errors['output'] }
-->

%include tail

