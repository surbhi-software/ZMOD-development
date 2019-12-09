import { Component, OnInit, ViewChild } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { finalize } from 'rxjs/operators';
import { MatTableDataSource, MatPaginator, MatSort } from '@angular/material';
import { animate, state, style, transition, trigger } from '@angular/animations';
//NN, AUTOML, PYTHON, SCORE
@Component({
    selector: 'app-tasks',
    templateUrl: './tasks.component.html',
    styleUrls: ['./tasks.component.scss'],
    animations: [
        trigger('detailExpand', [
            state('collapsed', style({ height: '0px', minHeight: '0', display: 'none' })),
            state('expanded', style({ height: '*' })),
            transition('expanded <=> collapsed', animate('225ms cubic-bezier(0.4, 0.0, 0.2, 1)')),
        ]),
    ],
})
export class TasksComponent implements OnInit {

    public isLoading = false;
    public isContentLoading = false;

    public listOfTasks: any = [];
    public selectedTask: any = {};
    public selectedHistory: any = {};
    public tabSelectedIndex = 0;
    public filter: any = '';

    public displayedColumnsTaskHistory: string[] = ['expand', 'executedAt', 'status'];
    public dataSourceTaskHistory: any = [];
    @ViewChild('taskHistoryMatPaginator') paginator: MatPaginator;
    @ViewChild('taskHistoryMatSort') sort: MatSort;

    public displayedColumnsGenerationResults: string[] = ['expand', 'modelName', 'score', 'bestmodel'];
    public dataSourceTaskHistoryGenerationResults: any = [];
    @ViewChild('generationResultsMatPaginator') paginatorGenerationResults: MatPaginator;
    @ViewChild('generationResultsMatSort') sortGenerationResults: MatSort;

    message = AlertMessages.TASK.deleteConfirmationTask;
    constructor(private apiService: HttpService, private utilService: UtilService) { }

    public changeSelectedIndex(index: number) {
        this.tabSelectedIndex = index;
    }

    public tabSelectedIndexChanged($event: any) {
    }

    public getAllTasks() {
        this.isLoading = true;
        this.listOfTasks = [];
        this.selectedTask = {};
        this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.task)
            .pipe(finalize(() => { this.isLoading = false; }))
            .subscribe(response => {
                // select first record by default
                if (response && response.length) {
                    this.listOfTasks = response;
                    this.selectTask(this.listOfTasks[0]);
                }
            });
    }

    public selectTask(selectedTaskData: any) {
        this.selectedTask = selectedTaskData;
        this.dataSourceTaskHistory = [];
        this.isContentLoading = true;
        this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.taskGet(this.selectedTask.id))
            .pipe(finalize(() => { this.isContentLoading = false; }))
            .subscribe(response => {
                this.selectedTask = response;
                this.dataSourceTaskHistory = new MatTableDataSource(response.history);
                this.dataSourceTaskHistory.paginator = this.paginator;
                this.dataSourceTaskHistory.sort = this.sort;
                //     this.dataSource.sort = this.sort;
                // this.selectedTask.status = response.status;
                // if (response.errorMessage) {
                //     this.selectedTask.errorMessage = response.errorMessage;
                //     this.taskCompleted = true;
                //     this.utilService.alert(AlertMessages.TASK.taskError);
                // } else if (this.selectedTask.type === 'NNProject' && response.tensorboardUrl) {
                //     this.tensorboardUrl = response.tensorboardUrl + '?t=' + Date.now();
                //     this.selectedTask.tensorboardUrl = response.tensorboardUrl + '?t=' + Date.now();
                //     this.taskCompleted = true;
                //     this.iframeLoaded();
                // } else if (this.selectedTask.type === 'AutoMLProject') {
                //     this.selectedTask.newPMMLFileName = response.newPMMLFileName;
                //     this.selectedTask.pmmlFilelocation = response.pmmlFilelocation;
                //     this.selectedTask.listOfModelAccuracy = response.listOfModelAccuracy;
                //     if (response.listOfModelAccuracy && response.listOfModelAccuracy.length) {
                //         this.dataSource = new MatTableDataSource(response.listOfModelAccuracy);
                //         this.taskCompleted = true;
                //     } else {
                //         this.dataSource = new MatTableDataSource(response.generationInfo);
                //     }
                //     this.dataSource.paginator = this.paginator;
                //     this.dataSource.sort = this.sort;
                // } else if (this.selectedTask.type === 'WeldGen') {
                //     this.selectedTask.information = response.information;
                //     if (this.selectedTask.status === 'Completed') {
                //         this.taskCompleted = true;
                //     }
                // } else if (this.selectedTask.type === 'PYTHON') {
                //     this.selectedTask.information = response.information;
                //     if (this.selectedTask.status === 'Complete') {
                //         this.taskCompleted = true;
                //     }
                // }
            });
    }

    public selectTaskHistory(selectedHistory: any) {
        console.log(selectedHistory);
        this.selectedHistory = selectedHistory;
        this.dataSourceTaskHistoryGenerationResults = [];
        this.isContentLoading = true;
        this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.taskGetHistory(this.selectedTask.id, selectedHistory.idforData))
            .pipe(finalize(() => { this.isContentLoading = false; }))
            .subscribe(response => {
                console.log(response);
                this.selectedTask.status = response.status;
                if (response.errorMessage) {
                    this.selectedTask.errorMessage = response.errorMessage;
                    this.utilService.alert(AlertMessages.TASK.taskError);
                } else {
                    if (this.selectedTask.type === 'AUTOML') {
                        this.dataSourceTaskHistoryGenerationResults = new MatTableDataSource(response.generationInfo);
                        this.dataSourceTaskHistoryGenerationResults.paginator = this.paginatorGenerationResults;
                        this.dataSourceTaskHistoryGenerationResults.sort = this.sortGenerationResults;
                        this.selectedHistory.pmmlFilelocation = response.pmmlFilelocation;
                        this.selectedHistory.newPMMLFileName = response.newPMMLFileName;
                        this.selectedHistory.status = response.status;
                    } else if (this.selectedTask.type === 'PYTHON') {
                        this.selectedTask.information = response.information;
                    } else if (this.selectedTask.type === 'NN' && response.tensorboardUrl) {
                        this.selectedTask.tensorboardUrl = response.tensorboardUrl + '?t=' + Date.now();
                        this.iframeLoaded();
                    }
                }
            });
    }

    public refreshTask() {
        this.selectTask(this.selectedTask);
    }

    public saveModel() {
        console.log(this.selectedHistory);
        const options = {
            body: {
                filePath: this.selectedHistory.pmmlFilelocation,
                fileName: this.selectedHistory.newPMMLFileName
            }
        };
        this.isContentLoading = true;
        this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.taskSaveModel(this.selectedHistory.idforData), options)
            .pipe(finalize(() => { this.isContentLoading = false; }))
            .subscribe(response => {
                this.utilService.alert(this.selectedHistory.newPMMLFileName + AlertMessages.TASK.save);
            });
    }

    public deleteTask() {
        this.isLoading = true;
        this.apiService.request(ApiRoutes.methods.DELETE, ApiRoutes.taskGet(this.selectedTask.id))
            .pipe(finalize(() => { this.isLoading = false; }))
            .subscribe(response => {
                this.getAllTasks();
                this.utilService.alert(AlertMessages.TASK.delete);
            });
    }

    public stopTask() {
        this.isLoading = true;
        this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.taskStop(this.selectedTask.id))
            .pipe(finalize(() => { this.isLoading = false; }))
            .subscribe(response => {
                this.selectedTask = response;
                this.utilService.alert(AlertMessages.TASK.taskStopped);
            });
    }

    public toggleSidebar(action: string) {
        this.utilService.toggleSidebar(action);
    }

    public iframeLoaded() {
        try {
            const ifrm: HTMLIFrameElement = document.getElementById('tb') as HTMLIFrameElement;
            const ifrmDoc = ifrm.contentDocument ? ifrm.contentDocument : ifrm.contentWindow.document;
            const ifrmHeader = ifrmDoc.getElementById('toolbar');
            ifrmHeader.style.backgroundColor = '#1776bf';
            console.log('iframe on load ', ifrm, ifrmDoc, ifrmHeader);
        } catch (err) {
            console.log(err);
        }
    }

    ngOnInit() {
        this.getAllTasks();
    }
}
