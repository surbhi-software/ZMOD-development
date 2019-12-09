export const ApiRoutes = {
    methods: {
        POST: 'post',
        PUT: 'put',
        GET: 'get',
        DELETE: 'delete'
    },
    accountUserInfo: 'account/userInfo',
    accountLogout: 'account/logout',
    loginRedirect:'https://accounts.zmod.org/auth/realms/master/protocol/openid-connect/logout?post_logout_redirect_uri=' + location.origin + '&x-client-SKU=ID_NETSTANDARD2_0&x-client-ver=5.5.0.0', 

    data: 'data',
    dataGet: (id: string) => `data/${id}`,
    dataAutoML: (id: string) => `data/${id}/automl`,
    dataAutoMLAnomaly: (id: string) => `data/${id}/anamoly`,
    predictData: `data/predict`,
    scoreData: 'data/score',
    dataDownload: (id: string) => `data/${id}/download`,
    dataRename: (id: string) => `data/${id}/rename`,
    dataBaseImageForWelding: `data/baseImage`,
    generateImageForWelding: `data/generateImages`,

    models: 'model',
    modelCreate: 'model/create',
    modelGetLayers: `model/layers`,
    modelGet: (id: string) => `model/${id}`,
    modelEdit: (id: string) => `model/${id}/edit`,
    modelLoad: (id: string) => `model/${id}/load`,
    modelUnload: (id: string) => `model/${id}/unload`,
    modelTrain: (id: string) => `model/${id}/train`,
    modelUpdateLayer: (id: string) => `model/${id}/layer`,
    modelDownload: (id: string) => `model/${id}/download`,
    modelDeploy: (id: string) => `model/${id}/loadinzs`,
    modelDeployUndo: (id: string) => `model/${id}/unloadfromzs`,
    modelDeployed: 'model/deployed',
    modelLoaded: 'model/loaded',
    modelCompile: (id: string) => `model/${id}/compile`,
    modelRename: (id: string) => `model/${id}/rename`,

    code: 'code',
    codeGet: (id: string) => `code/${id}`,
    codeJupyter: (id: string) => `code/${id}/jupyter`,
    codeDownload: (id: string) => `code/${id}/download`,
    codeExecute: (id: string) => `code/${id}/execute`,
    codeRename: (id: string) => `code/${id}/rename`,

    task: 'task',
    taskGet: (id: number) => `task/${id}`,
    taskGetHistory: (id: string, historyId: string) => `task/${id}/history/${historyId}`,
    taskSaveModel: (id: number) => `task/${id}/saveModel`,
    taskStop: (id: number) => `task/${id}/stop`,

    instance: 'instances',
    instanceKill: (id: string) => `instances/${id}`,

    settings: 'setting'
};
