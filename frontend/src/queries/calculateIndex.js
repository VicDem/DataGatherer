import {defaultBaseUrl} from "../global_vars";
import axios from 'axios';
import getAuthAxiosConfig from "./common/getAuthAxiosConfig";

const fetchRecognizedTextFromImage = async (imgId, fieldName) => {

    let base = process.env.REACT_APP_API_URL || defaultBaseUrl

    const {data} = await axios.get(
        base + `/b/storage_api/img_crops/?image=${imgId}&fieldName=${fieldName}`,
        await getAuthAxiosConfig(),
    )

    if (!Array.isArray(data)){
        throw Error("the result is not an array!")
    }

    if (data.length === 1){
        return data[0]
    }

    return null

}

export default fetchRecognizedTextFromImage