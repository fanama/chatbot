<script lang="ts">


  export let message: string;

</script>

<div
  class={`message flex items-start space-x-4 mb-4`}
>
  <div
    class={`bg-gradient-to-br from-blue-200 to-white text-blue-900 p-4 rounded-lg  w-fit overflow-auto `}
  >
      {message}


    
</div>
</div>