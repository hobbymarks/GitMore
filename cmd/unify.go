/*
Copyright © 2022 hobbymarks ihobbymarks@gmail.com
*/
package cmd

import (
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strings"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"golang.org/x/term"
	"gopkg.in/ini.v1"
)

// unifyCmd represents the unify command
var unifyCmd = &cobra.Command{
	Use:   "unify",
	Short: "Unify git directory name",
	Long: `changing local GitRepoDirectory name to GitRepoName@OrganizationName:
ProjectDir ==> GitRepoName@OrganizationName
GiatLocalDir ==> giat@hobbymarks
...`,
	Run: func(cmd *cobra.Command, args []string) {
		inplace, err := cmd.Flags().GetBool("inplace")
		if err != nil {
			log.Fatal(err)
		}
		cfm, err := cmd.Flags().GetBool("confirm")
		if err != nil {
			log.Fatal(err)
		}

		PrintTipFlag := false

		gitDirs, err := AllGitDirs(args)
		if err != nil {
			log.Error(err)
			return
		}
		unifyGitRepo := func(gdir string, gro string) {
			dir, _ := filepath.Split(gdir)
			if err := os.Rename(gdir, filepath.Join(dir, gro)); err != nil {
				log.Error(err)
			} else {
				fmt.Printf("%s==>%s\n", gdir, gro)
			}
		}
		frds, err := FreezedGiatRecords()
		if err != nil {
			log.Fatal(err)
		}
		log.Trace(frds)
		for _, gdir := range gitDirs {
			if rURL, gro, err := DecodeGitConfig(filepath.Join(gdir, ".git/config")); err != nil {
				log.Error(err)
			} else {
				if len(gro) == 0 {
					continue
				}
				if ok := ArrayContainsElemenet(frds, filepath.Base(gdir)+rURL); ok {
					log.Trace("Freezed:" + filepath.Base(gdir) + rURL)
					continue
				}
				_, file := filepath.Split(gdir)
				if file == gro {
					log.Trace("NoNeed:", gdir)
					continue
				}
				if inplace {
					unifyGitRepo(gdir, gro)
				} else {
					fmt.Printf("%s-->%s\n", gdir, gro)
					if cfm {
						switch confirm() {
						case A, All:
							inplace = true
							unifyGitRepo(gdir, gro)
						case Y, Yes:
							unifyGitRepo(gdir, gro)
						case N, No:
							// PrintTipFlag = true
							continue
						case Q, Quit:
							os.Exit(0)
						}
					} else {
						PrintTipFlag = true
					}
				}
			}
		}
		if PrintTipFlag {
			noEffectTip()
		}
	},
}

func init() {
	rootCmd.AddCommand(unifyCmd)

	unifyCmd.Flags().BoolP("confirm", "c", false, "Confirm unify git direcotry name")
	unifyCmd.Flags().BoolP("inplace", "i", false, "Unify git direcotry name inplace")
}

// return remoteURL,gitRepoName,err
func DecodeGitConfig(configPath string) (string, string, error) {
	cfg, err := ini.Load(configPath)
	if err != nil {
		return "", "", err
	}

	// pattern := regexp.MustCompile(`(github.com/(?P<org>\S+)/(?P<repo>\S+).git)|(github.com/(?P<org>\S+)/(?P<repo>\S+))`)
	pattern := regexp.MustCompile(`(//(\S+)/(?P<org>\S+)/(?P<repo>\S+).git)|(//(\S+)/(?P<org>\S+)/(?P<repo>\S+))`)
	template := []byte("$repo@$org")
	result := []byte{}

	content := []byte(cfg.Section(`remote "origin"`).Key("url").String())
	for _, submatches := range pattern.FindAllSubmatchIndex(content, -1) {
		result = pattern.Expand(result, template, content, submatches)
	}
	gr := string(result)
	log.Trace(gr)

	return string(content), gr, nil
}

func confirm() UserInput {
	var cmsg string

	fmt.Print("Please confirm (all,yes,no,quit):")
	fmt.Scan(&cmsg)

	return UserInput(strings.ToLower(cmsg))
}

type UserInput string

const (
	All  UserInput = "all"
	A    UserInput = "a"
	Yes  UserInput = "yes"
	Y    UserInput = "y"
	No   UserInput = "no"
	N    UserInput = "n"
	Quit UserInput = "quit"
	Q    UserInput = "q"
)

func noEffectTip() {
	var tipsDivider string

	if term.IsTerminal(0) {
		if tw, _, err := term.GetSize(0); err != nil {
			log.Error(err)
			tipsDivider = strings.Repeat("*", 80)
		} else {
			tipsDivider = strings.Repeat("*", tw)
		}
		fmt.Println(tipsDivider)
		fmt.Println("--> 'will change to' ==> 'changed to',in order to take effect,add flag '-i' or '-c'")
	}
}
