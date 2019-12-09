import { Component, OnInit } from '@angular/core';
import { UtilService, HttpService, ApiRoutes } from '../../shared';
import { SwUpdate } from '@angular/service-worker';
import { Router } from '@angular/router';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  public userInfo: any = {};
  public isNavOpen = true;
  public title = '';
  public urlCockpit = '';
  public urlDeviceManagment = '';
  constructor(private swUpdate: SwUpdate,
    private utilService: UtilService,
    private apiService: HttpService,
    private router: Router) {
    this.router.events.subscribe(() => {
      console.log(this.router.url.substr(1));
      this.title = this.router.url.substr(1);
    });
  }
  navOpen() {
    this.utilService.toggleSidebar('MENU');
    this.isNavOpen = !this.isNavOpen;
  }
  checkUpdate() {
    if (this.swUpdate.isEnabled) {
      this.swUpdate.available.subscribe((event) => {
        this.utilService.alert('New version available', 'Update', true)
          .onAction().subscribe(() => {
            window.location.reload();
          });
      });
    }
  }
  getUserInfo() {
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.accountUserInfo)
      .subscribe(response => {
        this.userInfo = response;
      });
  }
  logout() {
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.accountLogout)
      .subscribe(response => {
        console.log('explicitly redirecting to login page');
        this.goToUrl(ApiRoutes.loginRedirect);
      });
  }
  goToUrl(URL: any) {
    window.location.href = URL;
  }
  public updateUrl() {
    const settingsJSON = localStorage.getItem('settingsJSON');
    const c8ySelectedObj: any = this.utilService.getSettingsObject('C8Y', JSON.parse(settingsJSON));
    if (c8ySelectedObj && c8ySelectedObj.url) {
      this.urlCockpit = `${c8ySelectedObj.url}/apps/cockpit`;
      this.urlDeviceManagment = `${c8ySelectedObj.url}/apps/devicemanagement`;
    } else {
      this.utilService.alert('Cumulocity credentials not defined.');
    }
  }
  public getSettings() {
    this.apiService.request(ApiRoutes.methods.GET, ApiRoutes.settings)
      .subscribe(response => {
        console.log(response);
        localStorage.setItem('settingsJSON', JSON.stringify(response));
        const c8ySelectedObj: any = this.utilService.getSettingsObject('C8Y', response);
        if (c8ySelectedObj && c8ySelectedObj.url) {
          this.urlCockpit = `${c8ySelectedObj.url}/apps/cockpit`;
          this.urlDeviceManagment = `${c8ySelectedObj.url}/apps/devicemanagement`;
        } else {
          this.utilService.alert('Cumulocity credentials not defined.');
        }
      });
  }

  ngOnInit() {
    this.checkUpdate();
    this.getUserInfo();
    this.getSettings();
  }
}
