import {defaultBaseUrl} from "../global_vars";
import axios from 'axios';
import getAuthAxiosConfig from "./common/getAuthAxiosConfig";

const calculateIndex = async () => {

    let base = process.env.REACT_APP_API_URL || defaultBaseUrl

    await axios.get(
        base + `/b/fx_api/compute_index/`,
        await getAuthAxiosConfig(),
    ).then((res) => {
        console.log(res.data)
    })

}

export default calculateIndex