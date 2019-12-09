import { Component, OnInit, EventEmitter, Output, ViewChild } from '@angular/core';
import { ApiRoutes, HttpService, UtilService, AlertMessages } from '../../shared';
import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-repo',
  templateUrl: './repo.component.html',
  styleUrls: ['./repo.component.scss']
})
export class RepoComponent implements OnInit {
  public nyokaRemote: any = {};
  public isContentLoading = false;
  constructor(private apiService: HttpService, private utilService: UtilService) { }
  public getSettings() {
    this.isContentLoading = true;
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.settings)
      .pipe(finalize(() => { this.isContentLoading = false; }))
      .subscribe(response => {
        console.log(response);
        this.nyokaRemote = this.utilService.getSettingsObject('NR', response);
        console.log(this.nyokaRemote);
        if (this.nyokaRemote && this.nyokaRemote.url) {
          console.log(this.nyokaRemote.url);
        } else {
          this.utilService.alert('Remote url is not defined.');
        }
      });
  }
  ngOnInit() {
    this.getSettings();
  }
  public toggleSidebar(action: string) {
    this.utilService.toggleSidebar(action);
  }

}
