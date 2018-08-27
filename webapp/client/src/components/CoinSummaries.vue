<template>
<div>
    <div v-if="coins.length > 0">
        <coin-summaries-table :items="coins"/>
    </div>
    <div v-else>
        Loading coin summaries...
    </div>
</div>
</template>


<script>
export default {
    props: ['coins'],
}
</script>
