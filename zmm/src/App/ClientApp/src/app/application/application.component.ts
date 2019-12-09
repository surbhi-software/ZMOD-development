import { Component, OnInit, ViewChild } from '@angular/core';
import { UtilService } from '../shared';
import { MatSidenav } from '@angular/material';

@Component({
  selector: 'app-application',
  templateUrl: './application.component.html',
  styleUrls: ['./application.component.scss']
})
export class ApplicationComponent implements OnInit {

  public sidenavOptions = {
    bottom: 0,
    fixed: false,
    top: 0
  };
  public onlineAlert: any;
  @ViewChild('sidenav') public sidenav: MatSidenav;

  constructor(private utilService: UtilService) { }

  ngOnInit() {
    this.utilService.sidebarAction.subscribe((action) => {
      if (action === 'MENU') {
        this.sidenav.toggle();
      }
      if (action === 'FULLSCREEN') {
        this.sidenav.open();
      }
      if (action === 'FULLSCREEN_EXIT') {
        this.sidenav.close();
      }
    });
    this.utilService.checkInternetConnection().subscribe(async (online) => {
      const isOnline = await online;
      if (isOnline && this.onlineAlert) {
        this.onlineAlert.dismiss();
      } else if (!isOnline) {
        this.onlineAlert = this.utilService.alert('You are offline. Some functionality may be unavailable.', '', true);
      }
    });
  }
}
