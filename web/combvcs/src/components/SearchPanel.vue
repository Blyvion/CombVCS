<template>
    <v-row class="justify-center">
        <v-overlay v-model="busy" z-index="999">
            <v-progress-linear indeterminate size="200"></v-progress-linear>
        </v-overlay>
        <v-col cols="10" lg="6" class="d-flex justify-center pb-6">
            <v-text-field
                label="Search"
                outlined
                rounded
                clearable
                v-model="searchText"
                prepend-inner-icon="mdi-magnify"
                dense
                hide-details
                class="mr-4"
                @keydown.enter="executeSearch"
            >
            </v-text-field>
            <v-btn color="primary" @click="executeSearch" rounded>Search</v-btn>
        </v-col>
    </v-row>
</template>
<script>
import axiosApi from "../utils/axios-instance";
export default {
    name: "SearchPanel",
    props: {
        videoName: { type: String }
    },
    data() {
        return {
            searchText: null,
            busy: false,
        }
    },
    methods: {
        executeSearch() {
            if (!this.searchText || !this.videoName) return;
            this.busy = true;
            let formData = new FormData();
            formData.append("text", this.searchText);
            formData.append("filename", this.videoName);
            return axiosApi({
                url: "search",
                method: "POST",
                data: formData,
            }).then((response) => {
                console.log(response);
                this.busy = false;
                this.$emit("search");
            }).catch((error) => {
                this.busy = false;
                console.log(error);
            })
        },
    }
}
</script>
