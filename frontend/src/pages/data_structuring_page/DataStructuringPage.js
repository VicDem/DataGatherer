import SingleImgAnalysisLayout from "../../layouts/single_image_analysis_layout/SingleImgAnalysisLayout";
import ReactCrop from "react-image-crop";
import bolletta from "../bolletta.jpeg";
import ImageAnalysisCard from "../../components/analysis/ImageAnalysisCard";
import Card from "../../components/generic/Card";
import DataAnalysisCard from "../../components/analysis/DataAnalysisCard";
import {useSearchParams} from "react-router-dom";
import {useRef, useState} from "react";
import {useMutation, useQuery} from "@tanstack/react-query";
import fetchImageData from "../../queries/fetchImageData";
import {saveReviewedData} from "../../queries/saveReviewedData";
import {defaultBaseUrl} from "../../global_vars";
import UsernameAnalysisCard from "../../components/analysis/UsenameAnalysisCard";
import HashtagAnalysisGallery from "../../components/analysis/HashtagAnalysisGallery";
import {useCookies} from "react-cookie";
import fetchProject from "../../queries/fetchProject";

const DataStructuringPage = () => {
    const [searchParams] = useSearchParams();
    const imageId = searchParams.get("img_id");

    const [cookies] = useCookies(['current_prj']);

    const { data: imgData, error, isFetching} = useQuery({
        queryKey: ['oiok', imageId],
        queryFn: () => (fetchImageData(imageId))
    });

    const {data: projectData, isSuccess: isProjectDataSuccess} = useQuery({
        queryKey: ['projectDataStructuringPage', imageId],
        queryFn: () => fetchProject(cookies.prjId),
        retry: 1
    })

    console.log(projectData)




    if (error) {
        return (
            <div>
                Error! {error.message}
            </div>
        )
    }

    if (isFetching){
        return (
            <div>
                Caricamento...
            </div>
        )
    }


    const baseUrl = process.env.REACT_APP_API_URL || defaultBaseUrl
    const imgUrl = baseUrl + imgData.image_file_url

    return (
        <SingleImgAnalysisLayout

            imageUserId={1}

            leftChildren={
                <div className={"w-100 h-100"}>
                    <img
                        className={"w-100 h-100 object-fit-contain"}
                        src={imgUrl}
                        alt={"Immagine in analisi"}
                    />
                </div>
            }

            rightChildren={
                <div>

                    <UsernameAnalysisCard imgId={imageId} />

                    <HashtagAnalysisGallery imgId={imageId}/>

                </div>
            }


            bottomChildren={
                <div className={"d-flex justify-content-center h-100 align-items-center bg-dark-subtle w-100"}>
                    <button style={{width: "20vw"}} className={"btn btn-primary my-2 mx-2"}
                            onClick={() => window.location.href = `/edit?img_id=${imageId}`}
                    >
                        Indietro
                    </button>
                    {
                        isProjectDataSuccess ?
                            <div>
                                {
                                    projectData.are_all_images_analyzed ?
                                        <button style={{width: "20vw"}}
                                                className={"btn btn-success my-2 mx-2"}
                                                disabled={true}
                                        >
                                            Tutte le immagini sono analizzate
                                        </button>
                                        :
                                        <button style={{width: "20vw"}}
                                                className={"btn btn-primary my-2 mx-2"}
                                                disabled={!isProjectDataSuccess}
                                                onClick={() => {
                                                    window.location.href = `/gather?img_id=${projectData.next_image_to_analyze}`
                                                }}
                                        >
                                            Analizza prox immagine
                                        </button>
                                }
                                <button style={{width: "20vw"}}
                                        className={"btn btn-primary my-2 mx-2"}
                                        disabled={!isProjectDataSuccess}
                                        onClick={() => {
                                            window.location.href = `/prj?id=${projectData.id}`
                                        }}
                                >
                                    Concludi
                                </button>
                            </div>
                        : <></>
                    }


                </div>
            }
        />
    )
}

export default DataStructuringPage