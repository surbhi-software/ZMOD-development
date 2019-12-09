import { Component, OnInit, ViewEncapsulation } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { Router } from '@angular/router';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-code',
  templateUrl: './code.component.html',
  styleUrls: ['./code.component.scss'],
  encapsulation: ViewEncapsulation.None
})

export class CodeComponent implements OnInit {
  public dropzoneConfig: any = {
    openFileBrowser: false,
    url: ApiRoutes.code,
    acceptedFiles: `.py,.ipynb,.jar,.R,.r`,
    acceptedFilesMsg: 'Allowed file types are : Python and Jupyter Notebook'
  };
  public editorOptions: any = {
    theme: 'vs-light',
    language: 'python'
  };
  public listOfCode: any = [];
  public selectedCode: any = {};
  public uploadFiles = false;
  public isLoading = false;
  public isContentLoading = false;
  public tabSelectedIndex = 0;
  message = AlertMessages.CODE.deleteConfirmationCode;
  public filter: any = '';
  public showExcuteFormPanel = false;

  constructor(private apiService: HttpService, private utilService: UtilService, private router: Router) { }

  public changeSelectedIndex(index: number) {
    this.tabSelectedIndex = index;
  }

  public uploadNewFiles() {
    if (this.tabSelectedIndex === 3) {
      this.dropzoneConfig.openFileBrowser = new Date();
    } else {
      this.dropzoneConfig.openFileBrowser = false;
      this.changeSelectedIndex(3);
      this.uploadFiles = true;
      this.selectedCode = {};
    }
  }

  public uploadFilesDone() {
    this.uploadFiles = false;
    this.changeSelectedIndex(0);
    this.getAllCode();
  }

  public getAllCode(refresh = false) {
    this.isLoading = true;
    const options = {
      params: {
        refresh: refresh
      }
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.code, options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.listOfCode = response;
        // select first record by default
        if (this.listOfCode && this.listOfCode.length && !this.uploadFiles) {
          this.selectCode(this.listOfCode[0]);
        } else if (!refresh) {
          this.uploadNewFiles();
        }
      }, err => {
        this.uploadNewFiles();
      });
  }

  public refresh() {
    this.getAllCode(true);
  }

  public selectCode(selectCode: any) {
    this.selectedCode = selectCode;
    this.uploadFiles = false;
    this.changeSelectedIndex(0);
  }

  public editCode() {
    this.isContentLoading = true;
    if (this.selectedCode.extension === 'py') {
      this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.codeGet(this.selectedCode.id))
        .pipe(finalize(() => { this.isContentLoading = false; }))
        .subscribe(response => {
          this.selectedCode = response;
          this.changeSelectedIndex(1);
        });
    } else {
      this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.codeJupyter(this.selectedCode.id))
        .pipe(finalize(() => { this.isContentLoading = false; }))
        .subscribe(response => {
          this.selectedCode.jupyterUrl = this.utilService.transformUrl(response.url);
          this.changeSelectedIndex(2);
        });
    }
  }

  public close() {
    this.changeSelectedIndex(0);
  }

  public saveCode() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.codeGet(this.selectedCode.id),
      {
        body: {
          fileContent: this.selectedCode.code
        }
      })
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.utilService.alert(AlertMessages.CODE.save);
      });
  }

  public updateName(name: any) {
    if (name.innerText === this.selectedCode.id) {
      return;
    }
    this.isLoading = true;
    const options = {
      body: {
        newName: name.innerText
      }
    };
    this.apiService.request(ApiRoutes.methods.PUT, ApiRoutes.codeRename(this.selectedCode.id), options)
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.selectedCode.id = response.id;
        this.selectedCode.name = response.name;
        this.selectedCode.url = response.url;
        this.selectedCode.filePath = response.filePath;
      }, errorResponse => {
        name.innerText = this.selectedCode.id;
      });
  }

  public deleteCode() {
    this.isLoading = true;
    this.apiService.request(ApiRoutes.methods.DELETE, ApiRoutes.codeGet(this.selectedCode.id))
      .pipe(finalize(() => { this.isLoading = false; }))
      .subscribe(response => {
        this.getAllCode();
        this.utilService.alert(AlertMessages.CODE.delete);
      });
  }

  public execute(formData: any) {
    if (this.showExcuteFormPanel) {
      this.isLoading = true;
      const options = {
        body: formData
      };
      this.apiService.request(ApiRoutes.methods.POST, ApiRoutes.codeExecute(this.selectedCode.id), options)
        .pipe(finalize(() => { this.isLoading = false; }))
        .subscribe(() => {
          this.utilService.alert(AlertMessages.CODE.execute);
          this.router.navigate(['tasks']);
        });
    } else {
      this.showExcuteFormPanel = true;
    }
  }
  public downloadCode() {
    this.isContentLoading = true;
    const options = {
      responseType: 'blob'
    };
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.codeDownload(this.selectedCode.id), options)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        this.utilService.saveFile(response, this.selectedCode.name);
        this.utilService.alert(AlertMessages.CODE.download);
      });
  }

  public onCodeUploadSuccess($event: any[]) {
    this.listOfCode = $event[1].concat(this.listOfCode);
  }

  public toggleSidebar(action: string) {
    this.utilService.toggleSidebar(action);
  }

  ngOnInit() {
    this.getAllCode();
  }

}
